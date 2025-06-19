"use client"
import React, { useState } from "react";
import { Button } from "./ui/button";
import Link from "next/link";
import { Input } from "./ui/input";
import { Bell, Mail, Menu, Search } from "lucide-react";
import Logo from "./logo";
import { Separator } from "./ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu";

const navLinks = [
    { name: "Browse Agents", href: "/browse" },
    { name: "Dashboard", href: "/dashboard" },
    { name: "Orders", href: "/orders" },
    { name: "Pricing", href: "/pricing" },
];

export const categories = [
    { name: "All", href: "/all" },           // for browsing everything
    { name: "Graphics & Design", href: "/graphics-design" }, // Logo Designer agent
    { name: "Code Fixes", href: "/code-fixes" },      // React Bug-Fixer agent
    { name: "Prompt Optimisation", href: "/prompt-optimisation" } // Prompt Optimiser agent
];

export default function Header() {
    const [menuOpen, setMenuOpen] = useState(false);
    const [avatarOpen, setAvatarOpen] = useState(false);

    return (
        <header className="sticky top-0 z-50 w-full bg-background">
            {/* Main nav bar */}
            <div className="flex py-4 items-center px-6 md:px-8 gap-2 md:gap-6">
                {/* Logo/wordmark */}
                <Logo />
                {/* Desktop search bar */}
                <form className="hidden md:flex flex-1 max-w-[560px] relative" role="search">
                    <Input
                        type="text"
                        placeholder="What agent do you need today?"
                        className="w-full rounded-full px-4 py-5 pr-10 text-sm focus:outline-none transition"
                        aria-label="Search agents"
                    />
                    <Button variant={""} size={"icon"} type="submit" className="absolute p-0 cursor-pointer right-1 top-1/2 -translate-y-1/2 rounded-full focus:outline-none" aria-label="Search">
                        <Search />
                    </Button>
                </form>
                <div className="flex items-center gap-1 md:gap-2 ml-auto">
                    <Button variant="ghost" size="icon" aria-label="Notifications" className="focus-visible:ring-2 rounded-full cursor-pointer hidden md:flex">
                        <Bell />
                    </Button>
                    <Button variant="ghost" size="icon" aria-label="Inbox" className="focus-visible:ring-2 rounded-full cursor-pointer hidden md:flex">
                        <Mail />
                    </Button>
                    {/* Avatar dropdown */}
                    <DropdownMenu open={avatarOpen} onOpenChange={setAvatarOpen}>
                        <DropdownMenuTrigger className="rounded-full">
                            <Avatar className="cursor-pointer">
                                <AvatarImage src="https://i.pravatar.cc/40" />
                                <AvatarFallback>CN</AvatarFallback>
                            </Avatar>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent sideOffset={10} align="end">
                            <Link href="/profile">
                                <DropdownMenuItem className="cursor-pointer">
                                    Profile
                                </DropdownMenuItem>
                            </Link>
                            <Link href="/settings">
                            <DropdownMenuItem className="cursor-pointer">
                                Settings
                            </DropdownMenuItem>
                            </Link>
                            <Link href="/logout">
                            <DropdownMenuItem className="cursor-pointer">
                                Logout
                            </DropdownMenuItem>
                            </Link>
                        </DropdownMenuContent>
                    </DropdownMenu>
                    <div className="relative">
                        {/* {avatarOpen && (
                            // <div className="absolute right-0 mt-2 w-40 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded shadow-lg py-1 z-50 animate-fade-in">
                            //     <a href="/profile" className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">Profile</a>
                            //     <a href="/settings" className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">Settings</a>
                            //     <button className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400">Logout</button>
                            // </div>
                        )} */}
                    </div>
                    {/* Hamburger (sm only) */}
                    <Button
                        className="md:hidden ml-2 rounded-full focus:outline-none focus-visible:ring-2 cursor-pointer"
                        aria-label="Open menu"
                        onClick={() => setMenuOpen(v => !v)}
                        size={"icon"}
                        variant={"outline"}
                    >
                        <Menu />
                    </Button>
                </div>
            </div>
            {/* Mobile search bar */}
            <form className="flex md:hidden px-4 pb-2" role="search">
                <Input
                    type="text"
                    placeholder="What agent do you need today?"
                    className="w-full rounded-full border px-4 py-5 pr-10 text-sm focus:outline-none transition"
                    aria-label="Search agents"
                />
                <Button variant={""} size={"icon"} type="submit" className="-ml-10 p-2 rounded-full" aria-label="Search">
                    <Search />
                </Button>
            </form>
            {/* Mobile nav menu */}
            {/* {menuOpen && (
                <nav className="md:hidden px-4 pb-2 animate-fade-in" aria-label="Mobile navigation">
                    {navLinks.map(link => (
                        <a
                            key={link.name}
                            href={link.href}
                            className="block px-2 py-2 text-base font-medium focus:outline-none focus-visible:ring-2  rounded transition-colors"
                        >
                            {link.name}
                        </a>
                    ))}
                </nav>
            )} */}
            {/* Category rail (sticky, scroll-hiding on sm) */}
            <Separator className={"my-3 sm:my-0"} />
            <div className="sticky top-14 my-2 md:top-[56px] z-40 bg-background overflow-x-auto whitespace-nowrap transition-transform duration-300 will-change-transform">
                <div className="flex gap-3 px-4 md:px-8 h-12 items-center text-sm">
                    {categories.map((cat, i) => (
                        <Link href={`/category/${cat.href}`} key={cat.name} className="py-1 transition-colors">
                            <Button variant={"outline"} className=" cursor-pointer rounded-full">{cat.name}</Button>
                        </Link>
                    ))}
                </div>
            </div>
            <Separator className={""} />
        </header>
    );
}