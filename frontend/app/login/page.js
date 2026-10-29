"use client";

import { useState } from "react";
import api from "@/lib/api";
import { saveTokens } from "@/lib/auth";
import { useRouter } from "next/navigation";


export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const router = useRouter();

    async function handleSubmit(e) {
        e.preventDefault();

        try {
            const res = await api.post("/auth/login", { email, password });
            console.log(res.data);
            saveTokens(res.data.accessToken, res.data.refreshToken);
            router.replace("/feed");
        } catch (err) {
            console.log(err.response?.data);
        }
    }

    return (
        <main>
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Log in</button>
            </form>
        </main>
    );
}