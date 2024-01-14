'use client'
import React, {useEffect} from "react"
import { useRouter } from "next/router"
import styles from '/VerificationForm.module.css'

const endpoint = 'http://localhost:8000/auth/verify'
// useState: instantiate VerificationData
const VerifyPage: React.FC = () => {
    const router = useRouter();
    const verify_token = router.query.verify_token as string

    useEffect(() => {
        const verifyUser = async () => {
            if (typeof verify_token === 'string') {
                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ verify_token }),
                    });
    
                    if (response.ok) {
                        // route to login on success
                        router.push("/login");
                    } else {
                        console.error("Verification failed");
                    }
                } catch (error) {
                    // error handling
                    console.error("Error - failed to verify: ", error);
                }
            }
        };
        verifyUser();
    }, [verify_token]);

    return (
        <div className={styles.status}> verifying user...</div>
    )
}
export default VerifyPage;
