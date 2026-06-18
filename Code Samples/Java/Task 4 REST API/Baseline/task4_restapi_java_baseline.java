package com.example.usermanagement;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@SpringBootApplication
public class UserManagementApi {
    public static void main(String[] args) {
        SpringApplication.run(UserManagementApi.class, args);
    }
}

class User {
    private int id;
    private String username;
    private String email;

    public User() {}

    public User(int id, String username, String email) {
        this.id = id;
        this.username = username;
        this.email = email;
    }

    public int getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public String getEmail() {
        return email;
    }

    public void setId(int id) {
        this.id = id;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}

@RestController
@RequestMapping("/users")
class UserController {

    private final Map<Integer, User> users = new HashMap<>();
    private int nextId = 1;

    @GetMapping
    public Collection<User> getAllUsers() {
        return users.values();
    }

    @GetMapping("/{id}")
    public User getUserById(@PathVariable int id) {
        return users.get(id);
    }

    @PostMapping
    public User createUser(@RequestBody User user) {
        user.setId(nextId++);
        users.put(user.getId(), user);
        return user;
    }

    @PutMapping("/{id}")
    public User updateUser(@PathVariable int id, @RequestBody User updatedUser) {
        User existingUser = users.get(id);

        if (existingUser != null) {
            existingUser.setUsername(updatedUser.getUsername());
            existingUser.setEmail(updatedUser.getEmail());
            users.put(id, existingUser);
        }

        return existingUser;
    }

    @DeleteMapping("/{id}")
    public String deleteUser(@PathVariable int id) {
        users.remove(id);
        return "User deleted successfully";
    }
}