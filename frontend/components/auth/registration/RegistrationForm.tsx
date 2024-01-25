'use client'
import React, { useState } from 'react';
import { UserRegistrationData } from './types';
import styles from './RegistrationForm.module.css'
import Link from 'next/link'

/*
    1. import typescript data structure (FastAPI schema)
    2. Use useState to manage component state (instantiate the schema)
    3. pass the structure into a component via Prop (pass instance of schema for use)
    4. access defined fields via the prop inside the component (accessing fields in instance of schema)
*/

const endpoint='http://localhost:8000/auth/register'
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{5,}$/;
const RegistrationForm = () => {

    // create the react component with useState
    const [userRegistrationData, setUserRegistrationData] = useState<UserRegistrationData>({
            email: '',
            fullname: '',
            username: '',
            phone_number: '',
            hashed_password: '',
    });
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('')

    //used for feedback on password requirements
    const [hasMinLength, setHasMinLength] = useState(false);
    const [hasUpper, setHasUpper] = useState(false);
    const [hasLower, setHasLower] = useState(false);
    const [hasNumber, setHasNumber] = useState(false);

    //realtime feedback for meeting password requirements
    const showPasswordTarget = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setUserRegistrationData({ ...userRegistrationData, hashed_password: value });

        // requirement validation
        setHasMinLength(value.length >= 5);
        setHasUpper(/[A-Z]/.test(value));
        setHasLower(/[a-z]/.test(value));
        setHasNumber(/\d/.test(value));
    };

    //checks if any fields are missing
    const fieldsPopulated = () => {
        return Object.values(userRegistrationData).every(value => value.trim() !== '')
    }


    // sends POST request 
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        //check if any fields are empty, kill function if so
        if(!fieldsPopulated()) {
            setErrorMessage("Fill in all fields to register")
            return;
        }

        //kill function if password doesn't meet requirements 
        if(!passwordRegex.test(userRegistrationData.hashed_password)) {
            setErrorMessage("Error - password does not meet requirements")
            return;
        }

        //check if password fields match, kill function if they don't
        if(confirmPassword!=userRegistrationData.hashed_password) {
            setErrorMessage("Passwords do not match")
            return;
        } else {
            // reset error message
            setErrorMessage('')
            try {
                const request = await fetch(endpoint, {
                    method:'POST',
                    headers: {'content-type':'application/json'},
                    //send body as json 
                    body: JSON.stringify(userRegistrationData),
                });

                if(request.ok) {
                    alert("A verification link has been sent to your email address with a 5 min expiration time.")
                } else {
                    const backendResponse = await request.json()
                    console.log(backendResponse)
                    setErrorMessage(backendResponse.detail || "An error occurred, try again")
                }
            } catch (error) {
                //TODO: better error handling 
                console.error("Registration unsuccessful: ", error)
            }
        }
    };

    // pass structure into component to access fields 
    return (
        <div>
            <h1 className={styles.title}>User Registration</h1>
            <form className={styles.authForm} onSubmit={handleSubmit}>
                <input 
                    className={styles.input}
                    type="text"
                    value={userRegistrationData.email}
                    onChange={(e) => setUserRegistrationData({ ...userRegistrationData, email: e.target.value })}
                    placeholder="Enter email address"
                />
                <input 
                    className={styles.input}
                    type="text"
                    value={userRegistrationData.fullname}
                    onChange={(e) => setUserRegistrationData({ ...userRegistrationData, fullname: e.target.value })}
                    placeholder="Enter your name"
                />
                <input 
                    className={styles.input}
                    type="text"
                    value={userRegistrationData.username}
                    onChange={(e) => setUserRegistrationData({ ...userRegistrationData, username: e.target.value })}
                    placeholder="Enter your username"
                />
                <input 
                    className={styles.input}
                    type="text"
                    value={userRegistrationData.phone_number}
                    onChange={(e) => setUserRegistrationData({ ...userRegistrationData, phone_number: e.target.value })}
                    placeholder="Enter your phone number"
                />
                <input 
                    className={styles.input}
                    type="password"
                    name="password"
                    value={userRegistrationData.hashed_password}
                    onChange={showPasswordTarget}
                    placeholder="Enter your password"
                />
                <input
                    className={styles.input}
                    type="password"
                    name="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                />            
                <button className={styles.button} type='submit'>Register</button>
                <div className={styles.buttonContainer}>
                <h2 className={styles.passwordTarget}>Password requirements</h2>
                    <div style={{ color: hasMinLength ? 'green' : 'red'}}>At least 5 characters</div>
                    <div style={{ color: hasUpper ? 'green' : 'red' }}>At least one uppercase letter</div>
                    <div style={{ color: hasLower ? 'green' : 'red' }}>At least one lowercase letter</div>
                    <div style={{ color: hasNumber ? 'green' : 'red' }}>At least one number</div>
                </div>
                <div className={styles.errorMessage}>{errorMessage}</div>
            </form>
            <div className={styles.buttonContainer}> Already have an account?
            <Link href="/auth/login" className={styles.button}>Log-in here</Link>
            </div>
        </div>
    );
};

export default RegistrationForm;