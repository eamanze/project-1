'use client';
import withAuth from '@/auth/withAuth';

function Dashboard() {
  return <h1>Protected Dashboard Page</h1>;
}

export default withAuth(Dashboard);
