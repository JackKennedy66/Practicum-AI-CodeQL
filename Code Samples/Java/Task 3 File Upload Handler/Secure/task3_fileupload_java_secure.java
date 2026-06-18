import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.MultipartConfig;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.*;
import java.util.Set;
import java.util.UUID;

@WebServlet("/upload")
@MultipartConfig(
        maxFileSize = 2 * 1024 * 1024,       // 2MB per file
        maxRequestSize = 3 * 1024 * 1024     // 3MB total request
)
public class SecureFileUploadHandler extends HttpServlet {

    private static final Path UPLOAD_DIR =
            Paths.get("C:/secure-uploads").toAbsolutePath().normalize();

    private static final Set<String> ALLOWED_TYPES = Set.of(
            "image/jpeg",
            "image/png",
            "application/pdf"
    );

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        Part filePart = request.getPart("file");

        if (filePart == null || filePart.getSize() == 0) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, "No file uploaded");
            return;
        }

        if (filePart.getSize() > 2 * 1024 * 1024) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, "File is too large");
            return;
        }

        String contentType = filePart.getContentType();

        if (!ALLOWED_TYPES.contains(contentType)) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, "File type not allowed");
            return;
        }

        Files.createDirectories(UPLOAD_DIR);

        String safeFileName = UUID.randomUUID().toString();

        String extension = switch (contentType) {
            case "image/jpeg" -> ".jpg";
            case "image/png" -> ".png";
            case "application/pdf" -> ".pdf";
            default -> throw new IOException("Unsupported file type");
        };

        Path destination = UPLOAD_DIR.resolve(safeFileName + extension).normalize();

        if (!destination.startsWith(UPLOAD_DIR)) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Invalid file path");
            return;
        }

        try (InputStream inputStream = filePart.getInputStream()) {
            Files.copy(inputStream, destination, StandardCopyOption.REPLACE_EXISTING);
        }

        response.setContentType("text/plain");
        response.getWriter().println("File uploaded successfully");
    }
}