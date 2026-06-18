import java.io.*;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import jakarta.servlet.annotation.WebServlet;

@WebServlet("/view-file")
public class FileViewerServlet extends HttpServlet {

    private static final String BASE_DIR = "C:/files/";

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String filename = request.getParameter("filename");

        response.setContentType("text/html");

        PrintWriter out = response.getWriter();
        out.println("<h2>File Viewer</h2>");
        out.println("<form method='GET'>");
        out.println("Filename: <input type='text' name='filename'>");
        out.println("<button type='submit'>View</button>");
        out.println("</form>");

        if (filename != null && !filename.isEmpty()) {
            File file = new File(BASE_DIR + filename);

            if (file.exists() && file.isFile()) {
                out.println("<h3>Contents of: " + filename + "</h3>");
                out.println("<pre>");

                BufferedReader reader = new BufferedReader(new FileReader(file));
                String line;

                while ((line = reader.readLine()) != null) {
                    out.println(line);
                }

                reader.close();
                out.println("</pre>");
            } else {
                out.println("<p>File not found.</p>");
            }
        }
    }
}