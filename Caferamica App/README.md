# Caferamica Android App

**Description:**  
This is a custom Android application developed exclusively for Caferamica Café to manage customer orders efficiently. It allows staff to track order status, update readiness and finalization, and automatically notify customers via SMS when their orders are ready. This app is not intended for general use.

**Key Features:**  
- Track orders by code with status: Ready, Finalized  
- Send automatic SMS notifications to customers when orders are ready  
- Batch processing of orders using letter + number ranges  
- Logs all actions in-app for easy tracking  
- Supports single and multiple order input modes  

**Technologies Used:**  
- Java (Android development)  
- Google Sheets API v4 for order data storage and retrieval  
- Google Service Account authentication for Sheets access  
- SMSManager for sending SMS notifications  
- Android Jetpack & Edge-to-Edge UI for modern UI handling  
- Java Time API for date/time formatting  

**Setup Instructions:**  
1. Place `account.json` (service account credentials) in the assets folder.  
2. Modify the existing `config.properties` in assets with your details.  
3. Request and grant SEND_SMS permission on the device.  
4. Build and run the app on an Android device.  

**This project demonstrates:**  
- Integration of Google APIs with Android  
- Handling real-time customer interactions via SMS  
- Managing dynamic data and order workflow automation  
- Designing a user-friendly UI with multiple input modes  

**Note:**  
This app is tailored specifically for Caferamica Café operations and is not a commercial product.
