package com.example.myapplication;

import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.widget.LinearLayout;
import android.Manifest;
import android.content.pm.PackageManager;
import android.telephony.SmsManager;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.ScrollView;

import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.LocalDate;

import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.services.sheets.v4.Sheets;
import com.google.api.services.sheets.v4.SheetsScopes;
import com.google.api.services.sheets.v4.model.ValueRange;
import com.google.auth.http.HttpCredentialsAdapter;
import com.google.auth.oauth2.GoogleCredentials;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import java.io.InputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Properties;

//-----------------------------------------------------------------------------------------------------------------

public class MainActivity extends AppCompatActivity
{
    private static final Log log = LogFactory.getLog(MainActivity.class);
    class OrderStatus
    {
        int rowNumber;
        String vasesNumber;
        boolean isReady;
        boolean isFinalized;
        String phoneNumber;
        OrderStatus(int row, String vases, boolean ready, boolean finalized, String phone)
        {
            this.rowNumber = row;
            this.vasesNumber = vases;
            this.isReady = ready;
            this.isFinalized = finalized;
            this.phoneNumber = phone;
        }
    }

    private Sheets sheetsService;
    private String sheetName = "";
    private String appName = "";
    private String spreadsheetId = "";
    private HashMap<String,OrderStatus> codMap = new HashMap<>();
    boolean isSingleLayout = true;
    LinearLayout multiLayout;
    TextView logText;
    Button readyButton;
    Button finalizedButton;
    Button statusButton;
    Button switchButton;
    ScrollView logScroll;
    EditText userText;
    EditText letterText;
    EditText fromText;
    EditText toText;

    //-----------------------------------------------------------------------------------------------------------------

    private void setupSheets() throws Exception
    {
        InputStream stream = getAssets().open("account.json");
        GoogleCredentials credentials = GoogleCredentials.fromStream(stream)
                .createScoped(Collections.singleton(SheetsScopes.SPREADSHEETS));
        sheetsService = new Sheets.Builder(
                GoogleNetHttpTransport.newTrustedTransport(),
                GsonFactory.getDefaultInstance(),
                new HttpCredentialsAdapter(credentials))
                .setApplicationName(appName)
                .build();
    }

    private void mapCodes() throws Exception
    {
        String range = sheetName + "!B:G";
        ValueRange response = sheetsService.spreadsheets().values().get(spreadsheetId, range).execute();
        List<List<Object>> values = response.getValues();

        if (values != null)
        {
            for (int i = 1; i < values.size(); i++)
            {
                List<Object> row = values.get(i);
                String cod = row.get(1).toString();

                String phone=row.get(0).toString();
                String vases = row.get(2).toString();
                boolean prepared = false;
                boolean finalized = false;
                if(row.size() > 4 && !row.get(4).toString().isEmpty())
                {
                    prepared = true;
                }
                if(row.size() > 5 && !row.get(5).toString().isEmpty())
                {
                    finalized = true;
                }

                OrderStatus status = new OrderStatus(i+1, vases, prepared, finalized, phone);
                codMap.put(cod,status);
            }
        }
    }

    private void logWrite(String a)
    {
        LocalTime otimp = LocalTime.now();
        DateTimeFormatter ptimp = DateTimeFormatter.ofPattern("HH:mm:ss");
        String timp = otimp.format(ptimp);
        runOnUiThread(()->
        {
            logText.post(()->logText.append("("+timp+ ")->"+a));
            logText.postDelayed(() -> logScroll.fullScroll(View.FOCUS_DOWN), 50);
        });
    }

    private void hideKeyboard()
    {
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        View currentFocus = getCurrentFocus();
        if (currentFocus != null)
        {
            imm.hideSoftInputFromWindow(currentFocus.getWindowToken(), 0);
        }
    }

    private void logHashMap()
    {
        for (HashMap.Entry<String, OrderStatus> entry : codMap.entrySet())
        {
            String code = entry.getKey();
            OrderStatus o = entry.getValue();

            logWrite("Cod: " + code + "\n"+
                    "   -Nr vase: " + o.vasesNumber + "\n"+
                    "   -Pregatit: " + (o.isReady ? "Da" : "Nu") + "\n"+
                    "   -Finalizat: " + (o.isFinalized ? "Da" : "Nu") + "\n"+
                    "   -Telefon: " + o.phoneNumber + "\n");
        }
    }

    private void checkStatus(String code)
    {
        if(code.isEmpty())
        {
            logWrite("Date incomplete.\n");
            return;
        }
        if(!codMap.containsKey(code))
        {
            logWrite("Comanda cu codul \""+ code +"\" nu exista.\n");
            return;
        }
        OrderStatus o = codMap.get(code);
        logWrite("Cod: " + code + "\n"+
                "   -Nr vase: " + o.vasesNumber + "\n"+
                "   -Pregatit: " + (o.isReady ? "Da" : "Nu") + "\n"+
                "   -Finalizat: " + (o.isFinalized ? "Da" : "Nu") + "\n"+
                "   -Telefon: " + o.phoneNumber + "\n");
    }

    private void processCodes(List<String> codes, View v, int index, int correctCount, int errorCount)
    {
        if (index >= codes.size())
        {
            if(codes.size()>1)
            {
                logWrite("Gasite si procesate corect: " + correctCount + "\n");
                logWrite("Negasite/neprocesate: " + errorCount + "\n");
                logWrite("Toate comenzile au fost verficate.\n");
            }
            return;
        }

        String code = codes.get(index);

        new Thread(() ->
        {
            try
            {
                if (!codMap.containsKey(code))
                {
                    if(code.isEmpty())
                    {
                        logWrite("Date insuficiente.");
                        runOnUiThread(() -> processCodes(codes, v, index + 1, correctCount, errorCount+1));
                        return;
                    }
                    logWrite("Comanda \"" + code + "\" nu există.\n");
                    runOnUiThread(() -> processCodes(codes, v, index + 1, correctCount, errorCount+1));
                    return;
                }

                OrderStatus comanda = codMap.get(code);
                int id = v.getId();
                boolean isReadyAction = id == R.id.buton1;
                boolean isFinalAction = id == R.id.buton2;
                boolean isStatusAction = id == R.id.buton3;

                if (isStatusAction)
                {
                    checkStatus(code);
                    runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount+1,errorCount));
                    return;
                }

                LocalDate today = LocalDate.now();
                String dateStr = today.format(DateTimeFormatter.ofPattern("dd/MM/yyyy"));
                ValueRange body = new ValueRange().setValues(
                        Collections.singletonList(Collections.singletonList(dateStr)));

                if (isReadyAction && !comanda.isReady)
                {
                    SmsManager sms = SmsManager.getDefault();
                    String SENT = "SMS_SENT_" + code;
                    String message = "Comanda dumneavoastră cu codul \"" + code + "\" este gata să fie ridicată!";
                    PendingIntent sentPI = PendingIntent.getBroadcast(
                            this, 0, new Intent(SENT), PendingIntent.FLAG_IMMUTABLE);

                    BroadcastReceiver br = new BroadcastReceiver()
                    {
                        @Override
                        public void onReceive(Context context, Intent intent)
                        {
                            unregisterReceiver(this);
                            if (getResultCode() == RESULT_OK)
                            {
                                logWrite("Mesaj trimis pentru " + code + ".\n");
                                new Thread(() ->
                                {
                                    try
                                    {
                                        String range = sheetName + "!F" + comanda.rowNumber + ":F" + comanda.rowNumber;
                                        sheetsService.spreadsheets().values()
                                                .update(spreadsheetId, range, body)
                                                .setValueInputOption("RAW")
                                                .execute();
                                        codMap.get(code).isReady = true;
                                        logWrite("Comanda \"" + code + "\" este pregătită.\n");
                                        runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount+1,errorCount));
                                    } catch (Exception e)
                                    {
                                        logWrite("Eroare Sheets: " + e + "\n");
                                        runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount,errorCount+1));
                                    }
                                }).start();
                            } else
                            {
                                logWrite("Eroare la trimiterea SMS pentru " + code + ".\n");
                                runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount,errorCount+1));
                            }
                        }
                    };

                    registerReceiver(br, new IntentFilter(SENT));
                    sms.sendTextMessage(comanda.phoneNumber, null, message, sentPI, null);
                }

                else if (isFinalAction && !comanda.isFinalized)
                {
                    String range = sheetName + "!G" + comanda.rowNumber + ":G" + comanda.rowNumber;
                    sheetsService.spreadsheets().values()
                            .update(spreadsheetId, range, body)
                            .setValueInputOption("RAW")
                            .execute();
                    codMap.get(code).isFinalized = true;
                    logWrite("Comanda \"" + code + "\" este finalizată.\n");
                    runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount+1,errorCount));
                }

                else
                {
                    logWrite("Comanda \"" + code + "\" era deja procesată pentru această acțiune.\n");
                    runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount,errorCount+1));
                }

            } catch (Exception e)
            {
                logWrite("Eroare la procesarea \"" + code + "\": " + e + "\n");
                runOnUiThread(() -> processCodes(codes, v, index + 1,correctCount,errorCount+1));
            }
        }).start();
    }

    private void buttonCodesProcess(View v)
    {
        hideKeyboard();
        if(isSingleLayout)
        {
            String cod = userText.getText().toString().trim().toUpperCase();
            userText.setText("");
            processCodes(Collections.singletonList(cod),v,0,0 ,0 );
        }
        else
        {
            String litera = letterText.getText().toString().trim().toUpperCase();
            String fromString = fromText.getText().toString().trim();
            String toString = toText.getText().toString().trim();
            if(!litera.isEmpty() && !fromString.isEmpty() && !toString.isEmpty() && litera.charAt(0)>='A' && litera.charAt(0)<='Z') {
                int from = Integer.parseInt(fromString);
                int to = Integer.parseInt(toString);
                letterText.setText("");
                fromText.setText("");
                toText.setText("");
                List<String> codes = new ArrayList<>();
                for (int i = from; i <= to; i++)
                {
                    codes.add(litera + i);
                }
                processCodes(codes,v,0, 0, 0);
            }
            else
            {
                logWrite("Date incomplete sau gresite.\n");
            }
        }
    }

    //-----------------------------------------------------------------------------------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // ---------- Initialize Views FIRST ----------
        logText = findViewById(R.id.logView);
        readyButton = findViewById(R.id.buton1);
        finalizedButton = findViewById(R.id.buton2);
        statusButton = findViewById(R.id.buton3);
        switchButton = findViewById(R.id.buton4);
        logScroll = findViewById(R.id.logScrol);
        userText = findViewById(R.id.user);
        multiLayout = findViewById(R.id.multipleInputLayout);
        letterText = findViewById(R.id.letterInput);
        fromText = findViewById(R.id.fromInput);
        toText = findViewById(R.id.toInput);

        // ---------- Request SMS permission ----------
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.SEND_SMS}, 1);
        }

        // ---------- Load config ----------
        try (InputStream input = getAssets().open("config.properties")) {
            Properties props = new Properties();
            props.load(input);

            spreadsheetId = props.getProperty("spreadsheet_id");
            sheetName = props.getProperty("sheet_name");
            appName = props.getProperty("app_name");

            logWrite("Config loaded successfully.\n");

        } catch (IOException e) {
            e.printStackTrace();
            logWrite("Error loading config: " + e.getMessage() + "\n");
        }

        // ---------- Start Sheets setup thread ----------
        new Thread(() -> {
            try {
                setupSheets();
            } catch (Exception e) {
                logWrite("Eroare setupsheets: " + e + "\n");
            }
            try {
                mapCodes();
            } catch (Exception e) {
                logWrite("Eroare mapcodes: " + e + "\n");
            }
        }).start();

        // ---------- Set listeners ----------
        letterText.setOnEditorActionListener((v, actionId, event) -> {
            fromText.requestFocus();
            return true;
        });

        fromText.setOnEditorActionListener((v, actionId, event) -> {
            toText.requestFocus();
            return true;
        });

        statusButton.setOnClickListener(this::buttonCodesProcess);
        readyButton.setOnClickListener(this::buttonCodesProcess);
        finalizedButton.setOnClickListener(this::buttonCodesProcess);
        switchButton.setOnClickListener(v -> {
            hideKeyboard();
            if (isSingleLayout) {
                userText.setVisibility(View.GONE);
                multiLayout.setVisibility(View.VISIBLE);
                userText.setText("");
            } else {
                userText.setVisibility(View.VISIBLE);
                multiLayout.setVisibility(View.GONE);
                letterText.setText("");
                fromText.setText("");
                toText.setText("");
            }
            isSingleLayout = !isSingleLayout;
        });
    }
}
