"use client";

import { useState , useEffect} from "react";
import api from "@/lib/api";

export default function SignupPage() {
    const title = "Create your account";
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    // const [confirmPassword, setConfirmPassword] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();
        try {
            const res = await api.post("/account", {
            name,
            email,
            password,
            // confirmPassword,
        });
        console.log(res.data);
        } catch (err) {
            console.log(err.response?.data);
        }
    }

    useEffect(() => {
        if(name === "parsa") {
           setName(name + "alizadeh")
        }
        // Any side effects needed on component mount
    }, [name]);

    return (
        <main>
            <h1>{title}</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="name">Name</label>
                    <input
                        id="name"
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
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
                        minLength={8}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                {/* <div>
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                    <p>{confirmPassword}</p>
                </div> */}
                <button type="submit">Sign up</button>
            </form>
        </main>
    );
}