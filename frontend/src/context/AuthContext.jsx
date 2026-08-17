import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/api";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // -----------------------------
    // Load existing logged-in user
    // -----------------------------
    useEffect(() => {
        const token = localStorage.getItem("token");

        if (!token) {
            setLoading(false);
            return;
        }

        api.get("/auth/me")
            .then((res) => {
                setUser(res.data);
            })
            .catch(() => {
                localStorage.removeItem("token");
                setUser(null);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    // -----------------------------
    // Login
    // -----------------------------
    const login = async (email, password) => {
        const form = new URLSearchParams();

        form.append("username", email);
        form.append("password", password);

        const response = await api.post(
            "/auth/login",
            form,
            {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            }
        );

        // Make sure backend returned a token
        const token = response.data?.access_token;

        if (!token) {
            throw new Error("Login succeeded but no access token was returned.");
        }

        // Save token BEFORE requesting /me
        localStorage.setItem("token", token);

        try {
            const meResponse = await api.get("/auth/me");

            setUser(meResponse.data);

            return meResponse.data;
        } catch (error) {
            // Login itself succeeded, but /me failed.
            // Remove invalid token so the application doesn't
            // remain in a broken authenticated state.
            localStorage.removeItem("token");
            setUser(null);

            throw error;
        }
    };

    // -----------------------------
    // Register
    // -----------------------------
    const register = async (data) => {
        const response = await api.post("/auth/register", data);
        return response.data;
    };

    // -----------------------------
    // Logout
    // -----------------------------
    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                login,
                logout,
                register,
                loading,
                authenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}