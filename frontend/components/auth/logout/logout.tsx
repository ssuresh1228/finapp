'use client'
import React, {useEffect} from 'react';
import styles from './logout.module.css'
import { useRouter } from 'next/navigation';

const endpoint = 'http://localhost:8000/auth/logout'

const handleLogout = async () => {
    const router = useRouter();

    // show confirmation dialog
    const isConfirmed = window.confirm("Are you sure you want to log out?");

    if (isConfirmed) {
        // logout confirmed, make a request to the logout endpoint
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                credentials: 'include', //using cookies
                headers:{'content-type': 'application/json'},
                body: null
            });

            if (response.ok) {
                router.push("/auth/login")
            } else {
                // Handle errors
                console.error('Logout failed');
            }
        } catch (error) {
            console.error('Logout request failed', error);
        }
    }
    return (
        <button className = {styles.button} onClick={handleLogout}>Logout</button>
    )
};



