import { Header } from "./Header";
import { TabBar } from "./TabBar";
import { Outlet } from "react-router";

export function Layout() {
  return (
    <>
      <Header />
      <div className="pb-20">
        <Outlet />
      </div>
      <TabBar />
    </>
  );
}
