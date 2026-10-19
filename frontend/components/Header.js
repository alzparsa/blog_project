import Link from "next/link";
import NavLink from "./NavLink";

export default function Header() {
    return (
        <header>
            
            <nav >
                <NavLink href="/">
                    <h1>Inspired!</h1>
                </NavLink>
                <NavLink href="/about">
                    About
                </NavLink>
                <NavLink href="/feed">
                    Feed
                </NavLink>
                <NavLink href="/teams">
                    My Teams
                </NavLink>
                <NavLink href="/categories">
                    My Categories
                </NavLink>
                <NavLink href="/login">
                    Login
                </NavLink>
            </nav>
        </header>
    );
}