import clase.Book;
import java.util.Scanner;
import java.util.ArrayList;
import java.io.File;
import java.io.FileWriter;
import java.util.HashMap;

public class bookManager {

    static File fd = new File("books.txt");
    static ArrayList<Book> booksList = new ArrayList<Book>();
    static HashMap<String, Book> booksMap = mapBooks();

    public static void showCase() {
        System.out.println("1. Add/update book");
        System.out.println("2. List books");
        System.out.println("3. Remove book");
        System.out.println("4. Sort books");
        System.out.println("0. Exit");
    }
    
    public static Book toBook(String line)
    {
        String regex = ";";
        String[] TAP = line.split(regex);
        Book myBook = new Book(TAP[0], TAP[1], Integer.parseInt(TAP[2]));
        return myBook;
    }

    public static HashMap<String, Book> mapBooks()
    {
        HashMap<String, Book> myMap = new HashMap<String, Book>();
        try(Scanner fileInput = new Scanner(fd))
        {
            while(fileInput.hasNextLine())
            {
                String line = fileInput.nextLine();
                Book myBook = new Book();
                myBook = toBook(line);
                myBook.index = booksList.size();
                myMap.put(myBook.title, myBook);
                booksList.add(myBook);
            }
        }catch(Exception e)
        {
            System.out.println("Error opening fileInput. " + e);
        }
        return myMap;
    }


    public static Book requestBook(Scanner userInput) 
    {
        System.out.println("Input title: ");
        String title = userInput.nextLine().trim();
        System.out.println("Input author: ");
        String author = userInput.nextLine().trim();
        int pages = 0;
        try {
            System.out.println("Input pages: ");
            pages = userInput.nextInt();
        } catch (Exception e) {
            System.out.println("Invalid nr of pages.(defaulted to 0)");
        }
        userInput.nextLine();
        Book myBook = new Book(title, author, pages);
        return myBook;
    }

//--------------1.--------------------------------------------------------
    public static void writeToList(Book myBook)
    {
        myBook.index = booksList.size();
        booksMap.put(myBook.title, myBook);
        booksList.add(myBook);
    }

//--------------2.--------------------------------------------------------
    public static void listBooks()
    {
        System.out.println();
        for(Book myBook : booksList)
        {
            System.out.println("Title: " + myBook.title + "; Author: " + myBook.author + "; Pages-Read: " + myBook.pagesRead);
        }
        System.out.println();
    }

//--------------3.--------------------------------------------------------

    public static void removeBook(String inp)
    {
        inp = inp.trim();
        Book b = booksMap.get(inp);
        if(b == null)
        {
            return;
        }
        int index = b.index;
        booksMap.remove(inp);
        booksList.remove(index);
        booksList.forEach( (book) -> 
        {
           if(book.index < index)
           {
                book.index--;
           }
        });
    }

//--------------4.--------------------------------------------------------

    public static void sortList(Scanner userInput)
    {
        System.out.println("Sort by: 1.Title  2.Author   3.Pages");
        int type = 0, ord = 1;
        try
        {
            type = userInput.nextInt();
            System.out.println("1.Ascending  2.Descending");
            int o = userInput.nextInt();
            userInput.nextLine();
            if(o==2){ord = -1;}
        }catch(Exception e){System.out.println("Invalid input.");}
        final int order = ord;
        switch(type)
        {
            case 1:
                booksList.sort((a,b) -> { return order*a.title.compareToIgnoreCase(b.title);});
                break;
            case 2:
                booksList.sort((a,b) -> { return order*a.author.compareToIgnoreCase(b.author);});
                break;
            case 3:
                booksList.sort((a,b) -> { return order*Integer.compare(a.pagesRead,b.pagesRead);});
                break;
        }
        for(int i = 0; i < booksList.size(); i++)
        {
           booksList.get(i).index = i;
        }
    }

    public static void updateFile()
    {
        try(FileWriter fw = new FileWriter(fd))
        {
            for(Book a : booksList)
            {
                fw.write(a.title + ";"+ a.author +";"+a.pagesRead+"\n");
            }
        }catch(Exception e)
        {
            System.out.println("Didn't open fw correctly.");
        }
    }


    public static void main(String[] args) {
        try (Scanner userInput = new Scanner(System.in)) {
            int caz = -1;
            while (caz != 0) {
                showCase();
                caz = -1;

                try {
                    caz = userInput.nextInt();
                    userInput.nextLine();
                }catch (Exception e){
                    System.out.println("Please enter a valid number");
                }

                switch(caz) {
                    case 1:
                        writeToList(requestBook(userInput));
                        break;
                    case 2:
                        listBooks();
                        break;
                    case 3:
                        System.out.println("Enter the title of the book to be removed:");
                        String title = userInput.nextLine();
                        removeBook(title);
                        break;
                    case 4:
                        sortList(userInput);
                        break;
                    case 0:
                        updateFile();
                        break;
                }

                
            }
        }catch(Exception e){
            System.out.println("UserInput didn't open correctly.");
        }
    }
}