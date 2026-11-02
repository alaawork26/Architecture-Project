import java.util.Scanner;

import java.util.Set;
import java.util.TreeSet;


public class KMapSimplifier {
    //عدد المتغيرات من 2 الي 5 (الثوابت)
    static final int MIN_VARIABLES = 2;
    static final int MAX_VARIABLES = 5;

    //ٌREAD NUMBER OF VARIABLES FROM USER INPUT
   static int readNumberOfVariabls(Scanner sc) {
    while (true) {               //بتفضل تسال لحد ما المستخدم يدخل رقم صحيح
        System.out.print("Enter number of variables ("
                + MIN_VARIABLES + "-" + MAX_VARIABLES + "): ");   //بتقرا السطر وتحوله لرقم صحيح
        try {                     //لو دخلنا حاجة مش رقم، هيرمي استثناء NumberFormatException
            int n = Integer.parseInt(sc.nextLine().trim());
            if (n >= MIN_VARIABLES && n <= MAX_VARIABLES) {
                return n;             //لو الرقم بين MIN و MAX (يتخرج، (نرجع الرقم         
            }
        } catch (NumberFormatException e) {     
            // لو كتبت حروف يتمسك الخطأ ومش بتقفل
        }
        System.out.println("Invalid! Please enter a number between "
                + MIN_VARIABLES + " and " + MAX_VARIABLES + ".");   //لما بيوصل هنا بترجع تسأل تاني
    }
}
//---------------------------------------------------

        //READ TERMS FROM USER INPUT
     public static Set<Integer>readTerms(String data, int max){
            
        Set<Integer> terms = new TreeSet<>();   //انشاء ال Set فاضي نحط فيه الارقام

        //للتأكد ان مدخلتش حاجة فاضية 
        if (data.trim().isEmpty()) {    
            return terms;   
        }

        try {                          //(\\s+") معناها مسافة او اكتر
            String[] values = data.trim().split("\\s+");       //   بتقسم النص عند اي مسافة

            /*  Enhance For loop 
              بتلف علي كل عنصر موجود في values
             وتحطه في value
            لو واحدة مش رقم صحيح هيرمي استثناء NumberFormatException */

            for(String value : values){
                int number = Integer.parseInt(value); //تحويل النص الي رقم صحيح

                if (number < 0 || number > max) {    //لو الرقم خارج النطاق المسموح بيه
                    return null;
                }
                //اضافة الرقم الي ال Set
                //لو الرقم صحيح وداخل النطاق المسموح بيه
                terms.add(number); 
            }
            //ارجاع ال Set بعد ما خلصنا من اضافة كل الارقام
            return terms;    /*---->>  لو set فاضي
                             معناها مفيش مدخلات، لو فيه ارقام معناها المدخلات صحيحة*/

        } catch (NumberFormatException e) {    //علشان الاخطاء لو دخلنا حاجة مش رقم
            return null;     //---->>> معناها مدخلات غلط
        }

    }

    //---------------------------------------------------

    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        //STEP 1: Read number of variables from user input
        int n = readNumberOfVariabls(sc);
        System.out.println("You chose " + n + " variables." );


        // STEP 2 : Calculate the maximum mimterm value
        int max = (int) Math.pow(2, n) - 1; // Maximum value for minterms
        
        //STEP 3: Read minterms from user input
        Set<Integer> minterms = null;
        
        while (minterms == null) {
            System.out.print("Enter minterms by spaces : ");
            String mintermInput = sc.nextLine();
            minterms = readTerms(mintermInput, max);

            if (minterms == null) {
                System.out.println("Invalid minterms!");
                System.out.println("Try again.");
            }
        }
             //STEP 4: Read don't care terms from user input
            Set<Integer> dontCares ;

            while (true) {
                System.out.print("Enter don't care terms by spaces (or press Enter if none): ");
                String dontCareInput = sc.nextLine();
                dontCares = readTerms(dontCareInput, max);

                if (dontCares == null) {
                    System.out.println("Invalid don't care terms!" );
                    System.out.println("Try again.");
                          continue;
                }

                boolean overlap = false;

                for (int term : dontCares) {     // بفحص لو في اي رقم من dontCares موجود في minterms
                    if (minterms.contains(term)) {
                        overlap = true;
                        break;
                    }
                }
                   /*لو في تداخل بين 
                   dontCares و minterms، 
                   هتظهر رسالة خطأ و هتفضل تسأل المستخدم لحد ما يدخل حاجة صحيحة*/
                if (overlap) {           
                    System.out.println("Error: Don't care terms cannot overlap with minterms.");
                    continue;
            }
        
                break;    
        }

        //STEP 5: Display input data
        System.out.println("\n====== K-Map Input Data ======");
        System.out.println("Number of variables: " + n);
        System.out.println("Minterms: " + minterms);
        System.out.println("Don't care terms: " + dontCares);
        sc.close();
    
    
    }
}    