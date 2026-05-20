import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-300 dark:bg-gray-950">
      <div className="flex flex-col items-center gap-6">
        <div className="text-center">
          <div className="text-5xl mb-3">🏦</div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            AWS Financial Services Assistant
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Sign in to access your workspace
          </p>
        </div>
        <SignIn />
      </div>
    </div>
  );
}
