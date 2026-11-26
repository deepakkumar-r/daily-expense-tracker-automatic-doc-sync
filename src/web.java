import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Dependency-free local web server for the Daily Expense Tracker frontend. */
public final class web {
    // Resolve frontend assets and local expense storage relative to the working directory.
    private static final Path ROOT = Path.of("src", "static").toAbsolutePath().normalize();
    private static final Path STORE = Path.of("expenses-java.json").toAbsolutePath().normalize();
    private static final Path STORE_TEMP = STORE.resolveSibling(STORE.getFileName() + ".tmp");
    private static final long MAX_CENTS = 99_999_999_999L;
    private static final int MAX_CATEGORY_LENGTH = 80;
    private static final int MAX_DESCRIPTION_LENGTH = 500;
    // Keep loaded expenses in memory and allocate IDs for new records.
    private static final List<Expense> expenses = new ArrayList<>();
    private static final AtomicLong nextId = new AtomicLong(1);
    private static final Pattern ID_PATH = Pattern.compile("^/api/expenses/(\\d+)$");

    // Store the formatted amount alongside integer cents to avoid floating-point rounding.
    private record Expense(long id, String amount, long cents, String category, String description, String date) {}

    /** Load saved data and start the HTTP server on the local device only. */
    public static void main(String[] args) throws Exception {
        load();
        // Route both API requests and frontend assets through a single handler.
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8000), 0);
        server.createContext("/", web::handle);
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
        System.out.println("Expense Tracker: http://127.0.0.1:8000/");
    }

    /** Restore records from the local JSON file; a missing file means a fresh tracker. */
    private static synchronized void load() throws IOException {
        if (!Files.exists(STORE)) return;
        String text = Files.readString(STORE);
        Matcher m = Pattern.compile("\\{\"id\":(\\d+),\"amount\":\"((?:\\\\.|[^\"\\\\])*)\",\"cents\":(\\d+),\"category\":\"((?:\\\\.|[^\"\\\\])*)\",\"description\":\"((?:\\\\.|[^\"\\\\])*)\",\"date\":\"((?:\\\\.|[^\"\\\\])*)\"\\}").matcher(text);
        // Read matching stored records and advance the next ID beyond existing records.
        while (m.find()) {
            long id = Long.parseLong(m.group(1));
            expenses.add(new Expense(id, unescape(m.group(2)), Long.parseLong(m.group(3)), unescape(m.group(4)), unescape(m.group(5)), unescape(m.group(6))));
            nextId.updateAndGet(value -> Math.max(value, id + 1));
        }
    }

    /** Serialize the current records and write them to local JSON storage. */
    private static synchronized void save() throws IOException {
        StringBuilder out = new StringBuilder("[");
        // Separate records with commas and escape text fields for JSON output.
        for (int i = 0; i < expenses.size(); i++) {
            Expense e = expenses.get(i);
            if (i > 0) out.append(',');
            out.append("{\"id\":").append(e.id()).append(",\"amount\":\"").append(json(e.amount()))
                .append("\",\"cents\":").append(e.cents()).append(",\"category\":\"").append(json(e.category()))
                .append("\",\"description\":\"").append(json(e.description())).append("\",\"date\":\"").append(json(e.date())).append("\"}");
        }
        Files.writeString(STORE_TEMP, out.append(']').toString(), StandardCharsets.UTF_8);
        try {
            Files.move(STORE_TEMP, STORE, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } catch (java.nio.file.AtomicMoveNotSupportedException error) {
            Files.move(STORE_TEMP, STORE, StandardCopyOption.REPLACE_EXISTING);
        }
    }

    /** Dispatch requests, translate failures into HTTP responses and close the exchange. */
    private static void handle(HttpExchange exchange) throws IOException {
        try {
            // Expense URLs use the JSON API; other URLs request frontend files.
            String path = exchange.getRequestURI().getPath();
            if (path.startsWith("/api/expenses")) handleApi(exchange, path);
            else serveStatic(exchange, path);
        } catch (IllegalArgumentException | ArithmeticException error) {
            // Report invalid input without exposing internal exception details.
            send(exchange, 400, "{\"error\":\"" + json(error.getMessage()) + "\"}");
        } catch (Exception error) {
            // Return a generic error for storage and other unexpected failures.
            send(exchange, 500, "{\"error\":\"Storage failure\"}");
        } finally {
            // Release the connection even when request handling fails.
            exchange.close();
        }
    }

    /** Handle listing, creating, updating and deleting expenses. */
    private static synchronized void handleApi(HttpExchange exchange, String path) throws IOException {
        String method = exchange.getRequestMethod();
        validateRequest(exchange, method);
        Matcher idMatch = ID_PATH.matcher(path);
        if ("GET".equals(method) && "/api/expenses".equals(path)) {
            // Apply optional month/category filters and return records in date/ID order.
            Map<String, String> query = query(exchange.getRequestURI().getRawQuery());
            String month = query.getOrDefault("month", "");
            String category = query.getOrDefault("category", "").trim().toLowerCase(Locale.ROOT);
            List<Expense> selected = expenses.stream().filter(e -> (month.isEmpty() || e.date().startsWith(month))
                && (category.isEmpty() || e.category().toLowerCase(Locale.ROOT).equals(category))).sorted(Comparator.comparing(Expense::date).thenComparingLong(Expense::id)).toList();
            send(exchange, 200, dashboard(selected));
            return;
        }
        if ("POST".equals(method) && "/api/expenses".equals(path)) {
            // Validate a new expense, persist it and return the created record.
            Map<String, String> body = body(exchange);
            Expense expense = create(body);
            expenses.add(expense);
            save();
            send(exchange, 201, "{\"expense\":" + expenseJson(expense) + "}");
            return;
        }
        if (idMatch.matches()) {
            // Look up the requested record before applying a record-specific operation.
            long id = Long.parseLong(idMatch.group(1));
            int index = indexOf(id);
            if (index < 0) throw new IllegalArgumentException("Expense not found");
            if ("DELETE".equals(method)) {
                // Remove the record and persist the remaining expenses.
                expenses.remove(index);
                save();
                send(exchange, 200, "{\"deleted\":\"" + id + "\"}");
                return;
            }
            if ("PUT".equals(method)) {
                // Validate supplied changes while retaining fields not included in the request.
                Map<String, String> body = body(exchange);
                Expense old = expenses.get(index);
                Expense updated = update(old, body);
                expenses.set(index, updated);
                save();
                send(exchange, 200, "{\"expense\":" + expenseJson(updated) + "}");
                return;
            }
        }
        // Reject routes or HTTP methods that this small API does not support.
        send(exchange, 405, "{\"error\":\"Method or path not supported\"}");
    }

    /** Validate required fields and assign an ID to a new expense. */
    private static Expense create(Map<String, String> body) {
        String amount = required(body, "amount");
        long cents = cents(amount);
        String category = required(body, "category").trim();
        String description = required(body, "description").trim();
        String date = body.getOrDefault("date", LocalDate.now().toString());
        // Require a valid calendar date and bounded category/description.
        validateText(category, "Category", MAX_CATEGORY_LENGTH);
        validateText(description, "Description", MAX_DESCRIPTION_LENGTH);
        validateDate(date);
        return new Expense(nextId.getAndIncrement(), format(cents), cents, category, description, date);
    }

    /** Merge supplied fields with an existing record and validate the result. */
    private static Expense update(Expense old, Map<String, String> body) {
        if (body.isEmpty()) throw new IllegalArgumentException("No fields to update");
        long cents = body.containsKey("amount") ? cents(body.get("amount")) : old.cents();
        String category = body.getOrDefault("category", old.category()).trim();
        String description = body.getOrDefault("description", old.description()).trim();
        String date = body.getOrDefault("date", old.date());
        validateText(category, "Category", MAX_CATEGORY_LENGTH);
        validateText(description, "Description", MAX_DESCRIPTION_LENGTH);
        validateDate(date);
        return new Expense(old.id(), format(cents), cents, category, description, date);
    }

    /** Convert a positive decimal amount into exact cents with checked arithmetic. */
    private static long cents(String value) {
        if (value == null || !value.matches("[0-9]+(\\.[0-9]{1,2})?")) throw new IllegalArgumentException("Invalid amount");
        // Split whole and fractional parts, padding a one-digit fraction to two digits.
        String[] parts = value.split("\\.", -1);
        long whole;
        try {
            whole = Long.parseLong(parts[0]);
        } catch (NumberFormatException error) {
            throw new IllegalArgumentException("Amount is too large");
        }
        long fraction = parts.length == 1 ? 0 : Long.parseLong((parts[1] + "00").substring(0, 2));
        // Reject overflow and zero amounts rather than silently producing invalid cents.
        long result = Math.addExact(Math.multiplyExact(whole, 100), fraction);
        if (result <= 0 || result > MAX_CENTS) throw new IllegalArgumentException("Amount must be between 0.01 and 999999999.99");
        return result;
    }

    /** Enforce loopback request headers and the mutation marker used by the frontend. */
    private static void validateRequest(HttpExchange exchange, String method) {
        String host = exchange.getRequestHeaders().getFirst("Host");
        if (host != null && !("127.0.0.1:8000".equalsIgnoreCase(host) || "localhost:8000".equalsIgnoreCase(host))) {
            throw new IllegalArgumentException("Host is not allowed");
        }
        String origin = exchange.getRequestHeaders().getFirst("Origin");
        if (origin != null && !("http://127.0.0.1:8000".equalsIgnoreCase(origin) || "http://localhost:8000".equalsIgnoreCase(origin))) {
            throw new IllegalArgumentException("Origin is not allowed");
        }
        if (!"GET".equals(method) && !"1".equals(exchange.getRequestHeaders().getFirst("X-Expense-Request"))) {
            throw new IllegalArgumentException("Missing X-Expense-Request header");
        }
    }

    /** Validate bounded text and dates before changing application state. */
    private static void validateText(String value, String label, int limit) {
        if (value.isEmpty()) throw new IllegalArgumentException(label + " is required");
        if (value.length() > limit) throw new IllegalArgumentException(label + " is too long");
    }

    private static void validateDate(String value) {
        if (!value.matches("\\d{4}-\\d{2}-\\d{2}")) throw new IllegalArgumentException("Invalid date");
        try {
            LocalDate.parse(value);
        } catch (DateTimeParseException error) {
            throw new IllegalArgumentException("Invalid date");
        }
    }

    /** Build the filtered dashboard payload, including chart series for the selected records. */
    private static String dashboard(List<Expense> selected) {
        long total = selected.stream().mapToLong(Expense::cents).sum();
        Map<String, Long> byDay = new LinkedHashMap<>();
        Map<String, Long> byCategory = new LinkedHashMap<>();
        for (Expense expense : selected) {
            byDay.merge(expense.date(), expense.cents(), Long::sum);
            byCategory.merge(expense.category(), expense.cents(), Long::sum);
        }
        StringBuilder out = new StringBuilder("{\"expenses\":[");
        // Serialize each filtered expense into the response array.
        for (int i = 0; i < selected.size(); i++) {
            if (i > 0) out.append(',');
            out.append(expenseJson(selected.get(i)));
        }
        // Include distinct sorted categories from the selected records.
        out.append("],\"categories\":[");
        List<String> categories = selected.stream().map(Expense::category).distinct().sorted().toList();
        for (int i = 0; i < categories.size(); i++) out.append(i == 0 ? "" : ",").append("\"").append(json(categories.get(i))).append("\"");
        // Send monetary totals as strings so JavaScript can preserve integer precision.
        out.append("],\"summary\":{\"total_cents\":\"").append(total).append("\",\"count\":").append(selected.size())
            .append(",\"category_count\":").append(categories.size()).append(",\"by_day\":[");
        int index = 0;
        for (Map.Entry<String, Long> entry : byDay.entrySet()) {
            if (index++ > 0) out.append(',');
            out.append("{\"date\":\"").append(json(entry.getKey())).append("\",\"amount_cents\":\"")
                .append(entry.getValue()).append("\"}");
        }
        out.append("],\"by_category\":[");
        index = 0;
        for (Map.Entry<String, Long> entry : byCategory.entrySet()) {
            if (index++ > 0) out.append(',');
            out.append("{\"category\":\"").append(json(entry.getKey())).append("\",\"amount_cents\":\"")
                .append(entry.getValue()).append("\"}");
        }
        out.append("]}}");
        return out.toString();
    }

    /** Serialize one expense using the field names expected by the frontend. */
    private static String expenseJson(Expense e) {
        return "{\"id\":\"" + e.id() + "\",\"amount\":\"" + e.amount() + "\",\"amount_cents\":\"" + e.cents()
            + "\",\"category\":\"" + json(e.category()) + "\",\"description\":\"" + json(e.description()) + "\",\"date\":\"" + e.date() + "\"}";
    }

    /** Serve the existing HTML, CSS and JavaScript files from the frontend directory. */
    private static void serveStatic(HttpExchange exchange, String path) throws IOException {
        String relative = "/".equals(path) ? "index.html" : path.substring(1);
        Path file = ROOT.resolve(relative).normalize();
        // Reject traversal outside the static directory and missing/non-file paths.
        if (!file.startsWith(ROOT) || !Files.isRegularFile(file)) { send(exchange, 404, "Not Found"); return; }
        // Set the asset content type and stream its bytes, closing the response afterwards.
        String type = relative.endsWith(".css") ? "text/css" : relative.endsWith(".js") ? "text/javascript" : "text/html";
        exchange.getResponseHeaders().set("Content-Type", type + "; charset=utf-8");
        byte[] bytes = Files.readAllBytes(file);
        exchange.sendResponseHeaders(200, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) { out.write(bytes); }
    }

    /** Extract string-valued request fields while honoring JSON string escapes. */
    private static Map<String, String> body(HttpExchange exchange) throws IOException {
        try (InputStream input = exchange.getRequestBody()) {
            String text = new String(input.readAllBytes(), StandardCharsets.UTF_8);
            Map<String, String> values = new LinkedHashMap<>();
            int[] position = {0};
            skipWhitespace(text, position);
            if (position[0] >= text.length() || text.charAt(position[0]++) != '{') throw new IllegalArgumentException("Invalid JSON body");
            while (true) {
                skipWhitespace(text, position);
                if (position[0] < text.length() && text.charAt(position[0]) == '}') {
                    position[0]++;
                    break;
                }
                String key = readJsonString(text, position);
                skipWhitespace(text, position);
                if (position[0] >= text.length() || text.charAt(position[0]++) != ':') throw new IllegalArgumentException("Invalid JSON body");
                skipWhitespace(text, position);
                values.put(key, readJsonString(text, position));
                skipWhitespace(text, position);
                if (position[0] >= text.length()) throw new IllegalArgumentException("Invalid JSON body");
                char separator = text.charAt(position[0]++);
                if (separator == '}') break;
                if (separator != ',') throw new IllegalArgumentException("Invalid JSON body");
            }
            return values;
        }
    }

    private static void skipWhitespace(String text, int[] position) {
        while (position[0] < text.length() && Character.isWhitespace(text.charAt(position[0]))) position[0]++;
    }

    private static String readJsonString(String text, int[] position) {
        if (position[0] >= text.length() || text.charAt(position[0]++) != '"') throw new IllegalArgumentException("Invalid JSON body");
        StringBuilder value = new StringBuilder();
        while (position[0] < text.length()) {
            char current = text.charAt(position[0]++);
            if (current == '"') return value.toString();
            if (current == '\\') {
                if (position[0] >= text.length()) throw new IllegalArgumentException("Invalid JSON body");
                char escaped = text.charAt(position[0]++);
                value.append(switch (escaped) {
                    case '"', '\\', '/' -> escaped;
                    case 'b' -> '\b';
                    case 'f' -> '\f';
                    case 'n' -> '\n';
                    case 'r' -> '\r';
                    case 't' -> '\t';
                    default -> throw new IllegalArgumentException("Invalid JSON escape");
                });
            } else {
                value.append(current);
            }
        }
        throw new IllegalArgumentException("Invalid JSON body");
    }

    /** Decode URL query parameters, accepting empty values and a missing query string. */
    private static Map<String, String> query(String raw) {
        Map<String, String> result = new LinkedHashMap<>();
        if (raw == null) return result;
        // Split each key/value only once so encoded values retain their contents.
        for (String item : raw.split("&")) {
            String[] pair = item.split("=", 2);
            result.put(URLDecoder.decode(pair[0], StandardCharsets.UTF_8), pair.length == 1 ? "" : URLDecoder.decode(pair[1], StandardCharsets.UTF_8));
        }
        return result;
    }

    /** Find a record's list position; return -1 when the ID does not exist. */
    private static int indexOf(long id) { for (int i = 0; i < expenses.size(); i++) if (expenses.get(i).id() == id) return i; return -1; }
    /** Require a field to be present; field-specific validation happens in the caller. */
    private static String required(Map<String, String> body, String key) { if (!body.containsKey(key)) throw new IllegalArgumentException("Missing " + key); return body.get(key); }
    /** Format positive integer cents as an amount with exactly two decimal places. */
    private static String format(long cents) { return (cents / 100) + "." + String.format(Locale.ROOT, "%02d", cents % 100); }
    /** Escape backslashes, quotes and newlines using the existing JSON helper. */
    private static String json(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t");
    }
    /** Decode the JSON escapes emitted by this server. */
    private static String unescape(String value) {
        return value.replace("\\\"", "\"").replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\\\", "\\");
    }
    /** Write a UTF-8 JSON response with the requested HTTP status. */
    private static void send(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        // Close the response stream automatically after sending the encoded body.
        try (OutputStream out = exchange.getResponseBody()) { out.write(bytes); }
    }
}
