import { Toaster as Sonner } from "sonner";

export function Toaster(props) {
  return <Sonner richColors closeButton theme="system" {...props} />;
}
