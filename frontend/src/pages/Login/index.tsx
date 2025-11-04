import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/context/ToastContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";

export const LoginPage = () => {
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await login(username, password);
      addToast({ title: "Welcome back!", variant: "success" });
      navigate("/dashboard", { replace: true });
    } catch (error) {
      addToast({
        title: "Login failed",
        description:
          error instanceof Error ? error.message : "Unexpected authentication error.",
        variant: "error"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-black via-[#191426] to-[#070B18] px-6">
      <div className="w-full max-w-md space-y-8 rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold text-white">Vibe Engine</h1>
          <p className="text-sm text-white/60">Sign in with developer credentials</p>
        </div>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                autoComplete="username"
                id="username"
                onChange={(event) => setUsername(event.target.value)}
                placeholder="admin"
                value={username}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                autoComplete="current-password"
                id="password"
                onChange={(event) => setPassword(event.target.value)}
                placeholder="admin"
                type="password"
                value={password}
              />
            </div>
          </div>
          <Button
            className="w-full"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? "Signing in…" : "Login"}
          </Button>
        </form>
        <p className="text-center text-xs text-white/40">
          Use the developer login (admin / admin) to access the control center.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
