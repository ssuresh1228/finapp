'use client'
import React, { useState} from "react";
import styles from "./ForgotPasswordForm.module.css"
import { UserEmail } from "./types";
import Link from "next/link";

const endpoint = 'http://localhost:8000/auth/forgot-password'

// form to enter email address
// clicking button sends password reset email to entered email address
const requestPasswordResetForm = () => {
    //create component with useState
    const[userData, setUserData] = useState<UserEmail>({
        email: ''
    });

    //sends get request to endpoint with user email 
    const handleSubmit = async(event: React.FormEvent) => {
        event.preventDefault()
        try{
            const response = await fetch(endpoint, {
                method:'POST',
                headers:{'content-type': 'application/json'},
                body: JSON.stringify(userData)
            })
            if(response.ok) {
                //if successful, call an alert
                alert("A link to reset your password has been sent to your email")
            } else {
                throw new Error(`${response.status}`);
            }
        }
        catch(error) {
            console.warn("An error occurred: ", error)
        }
    };

    //pass the structure into a component to access email field 
    return (
        <div>
            <form className={styles.ForgotPasswordForm} onSubmit={handleSubmit}>
                <input
                    className = {styles.input}
                    type="text"
                    name="email"
                    placeholder="Enter your email address"
                    value={userData.email}
                    onChange={(e) => setUserData({...userData, email: e.target.value})}
                />
                <button className={styles.button} type='submit'>Submit</button>
            </form>
            <Link href="/">
                <h1 className={styles.OutgoingLink}>
                    Go Home
                </h1>
            </Link>
            <Link href="/auth/register">
                <h1 className={styles.OutgoingLink}>
                    Register for an account here
                </h1>
            </Link>
        </div>
    )
}
export default requestPasswordResetForm;