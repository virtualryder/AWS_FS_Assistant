"use client";

/**
 * Syncs the Clerk session token into the api.ts module-level getter so that
 * all API calls and SSE streams include an Authorization header.
 * Renders nothing — drop it once in the root layout inside ClerkProvider.
 */

import { useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { setApiTokenGetter } from "@/lib/api";

export default function AuthTokenSync() {
  const { getToken, isSignedIn } = useAuth();

  useEffect(() => {
    if (isSignedIn) {
      // getToken() always returns a fresh JWT (Clerk handles refresh)
      setApiTokenGetter(() => getToken());
    } else {
      setApiTokenGetter(null);
    }
  }, [isSignedIn, getToken]);

  return null;
}
