import java.util.Scanner;

public class KMapSimplifier {
    //عدد المتغيرات من 2 الي 4 (الثوابت)
    static final int MIN_VARIABLES = 2;
    static final int MAX_VARIABLES = 4;

    static int readNumberOfVariabls(Scanner sc){
        while (true) {
            System.out.print("Enter number of variables (" 
                              + MIN_VARIABLES + "-" + MAX_VARIABLES + "): ");
            int n = sc.nextInt();
            if (n >= MIN_VARIABLES && n <= MAX_VARIABLES) {
                return n;
            }
            System.out.println("Invalid! Please enter a number between " 
                                + MIN_VARIABLES + "and" + MAX_VARIABLES + ".");

        }
        }
    
    
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);
        int n = readNumberOfVariabls(sc);
        System.out.println("You chose " + n + " variables." );
    }
}    