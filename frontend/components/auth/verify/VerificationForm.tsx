'use client'
import React, { useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import styles from './VerificationForm.module.css';

const VerifyPage = () => {
    const searchParams = useSearchParams();
    const router = useRouter();
    const endpoint = 'http://localhost:8000/auth/verify'

    //send post request with token 
    const verifyUser = async(backendToken: string) => {
      try {
        const response = await fetch(endpoint, {
          method:'POST',
          headers:{'content-type': 'application/json'},
          body: JSON.stringify({ verify_token: backendToken })
        });

        if(!response.ok){
          throw new Error('Error - verification failed');
        }

        // Redirect to login page on successful verification
        alert("ATTENTION: thank you for your attention")
        router.push('/auth/login')
      } catch (error) {
        console.log("Error caught: ", error)
      }
    }
    
    //get the token from URL and call verifyUser if token is valid
    useEffect(() => {
      const verify_token = searchParams.get("verify_token")
      if(verify_token) {
        verifyUser(verify_token)
        alert("Successfully verified, routing to login page")
      } else {
        console.error("Error - token is invalid or expired")
      }
    }, [searchParams]);


    return (
      <div className={styles.status}>
        verifying user...
      </div>
    );
};

export default VerifyPage;