import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.regex.Pattern;

import jakarta.servlet.*;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;

@WebServlet("/view-file")
public class SecureFileViewerServlet extends HttpServlet {

    private static final Path BASE_DIR = Paths.get("C:/safe-files").toAbsolutePath().normalize();

    private static final Pattern SAFE_FILENAME =
            Pattern.compile("^[a-zA-Z0-9._-]{1,100}$");

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws IOException {

        response.setContentType("text/html; charset=UTF-8");
        response.setHeader("X-Content-Type-Options", "nosniff");

        PrintWriter out = response.getWriter();

        out.println("<h2>Secure File Viewer</h2>");
        out.println("<form method='GET'>");
        out.println("Filename: <input type='text' name='filename'>");
        out.println("<button type='submit'>View</button>");
        out.println("</form>");

        String filename = request.getParameter("filename");

        if (filename == null || filename.isBlank()) {
            return;
        }

        if (!SAFE_FILENAME.matcher(filename).matches()) {
            out.println("<p>Invalid filename.</p>");
            return;
        }

        Path requestedFile = BASE_DIR.resolve(filename).normalize();

        if (!requestedFile.startsWith(BASE_DIR)) {
            out.println("<p>Access denied.</p>");
            return;
        }

        if (!Files.exists(requestedFile) || !Files.isRegularFile(requestedFile)) {
            out.println("<p>File not found.</p>");
            return;
        }

        if (!filename.endsWith(".txt")) {
            out.println("<p>Only .txt files are allowed.</p>");
            return;
        }

        out.println("<h3>File contents:</h3>");
        out.println("<pre>");

        try (BufferedReader reader = Files.newBufferedReader(requestedFile, StandardCharsets.UTF_8)) {
            String line;

            while ((line = reader.readLine()) != null) {
                out.println(escapeHtml(line));
            }
        }

        out.println("</pre>");
    }

    private String escapeHtml(String input) {
        return input
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#x27;");
    }
}