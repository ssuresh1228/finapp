import React from 'react';
import Link from 'next/link';
import styles from './homepage.module.css'

export default function Home() {
  return (
    <main>
      <h1 className={styles.title}>Root Page</h1>
      <div className={styles.buttonContainer}>
        <Link href="/auth/login" className={styles.button}>Login</Link>
        <Link href="/auth/register" className={styles.button}>Register</Link>
      </div>
    </main>
  );
}