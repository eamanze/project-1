import { CognitoUserPool } from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!, // e.g. us-east-1_XXXXXX
  ClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,      // e.g. abcdefgh123456789
};

export const userPool = new CognitoUserPool(poolData);
