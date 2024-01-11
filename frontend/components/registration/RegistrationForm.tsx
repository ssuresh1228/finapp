'use client'
import React, { useState } from 'react';
import { UserRegistrationData } from './types';
import styles from './RegistrationForm.module.css';

/*
    1. import typescript data structure (FastAPI schema)
    2. Use useState to manage component state (instantiate the schema)
    3. pass the structure into a component via Prop (pass instance of schema for use)
    4. access defined fields via the prop inside the component (accessing fields in instance of schema)
*/

const RegistrationForm = () => {
    // create the react component with useState
    const [userRegistrationData, setUserRegistrationData] = useState<UserRegistrationData>({
            email: '',
            fullname: '',
            username: '',
            phone_number: '',
            password: ''
    });

    // sends POST request 
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/auth/register', {
                method:'POST',
                headers: {'content-type':'application/json'},
                //send body as json 
                body: JSON.stringify(userRegistrationData),
            });

            if(!response.ok) {
                throw new Error(`${response.status}`);
            }

            // LOGGING
            const endpointResponse = await response.json();
            console.log(endpointResponse)

        } catch (error) {
            //TODO: better error handling 
            console.error("Registration unsuccessful: ", error)
        }
    };

    // pass structure into component to access fields 
    return (
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
                value={userRegistrationData.password}
                onChange={(e) => setUserRegistrationData({ ...userRegistrationData, password: e.target.value })}
                placeholder="Enter your password"
            />
            <button className={styles.button} type='submit'>Register</button>
        </form>
    );
};

export default RegistrationForm;