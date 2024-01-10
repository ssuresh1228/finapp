'use client'
import React, { useState } from 'react';
import styles from './AuthForm.module.css';

const AuthForm: React.FC = () => {
    const [email, setEmail] = useState('');
    const [fullname, setFullname] = useState('');
    const [username, setUsername] = useState('');
    const [phone_number, setPhoneNumber] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, fullname, username, phone_number, password }),
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }

            const data = await response.json();
            console.log(data)
            // TODO: Handle successful login here - redirect to main page

        } catch (err) {
            setError('Failed to login'); // basic error handling
            console.error(err);
        }
    };

    return (
        <form className={styles.authForm} onSubmit={handleSubmit}>
            {/* Form fields */}
            <input
                className={styles.input}
                type="text"
                onChange={(e) => setEmail(e.target.value)}
                placeholder='Enter your email address'
            />
            <input
                className={styles.input}
                type="text"
                onChange={(f) => setFullname(f.target.value)}
                placeholder='Enter your name'
            />
            <input
                className={styles.input}
                type="text"
                onChange={(g) => setUsername(g.target.value)}
                placeholder='Enter username'
            />
            <input
                className={styles.input}
                type="text"
                onChange={(h) => setPhoneNumber(h.target.value)}
                placeholder='Enter phone number'
            />
            <input
                className={styles.input}
                type="text"
                onChange={(i) => setPassword(i.target.value)}
                placeholder='Enter password'
            />

            <button className={styles.button} type="submit">Register</button>
        </form>
    );
};

export default AuthForm;
