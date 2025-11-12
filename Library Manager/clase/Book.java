package clase;

public class Book 
{
    public int index = 0;
    public String title;
    public String author;
    public int pagesRead = 0;

    public Book(String a, String b, int c) 
    {
        this.title = a;
        this.author = b;
        this.pagesRead = c;
    }
    
    public Book()
    {
        this.title = "";
        this.author = "";
        this.pagesRead = 0;
    }

    public String returnBook()
    {
        return("Title: "+ this.title + ";Author: "+ this.author +";Pages read: "+ this.pagesRead);
    }
}
