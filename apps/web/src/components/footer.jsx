import { menus } from "@/data/menus";
import { Button } from "./ui/button";
import Link from "next/link";
import Logo from "./logo";
import { IconBrandX, IconBrandDiscord, IconBrandGithub } from "@tabler/icons-react";
export default function Footer() {
    const socialLinks = [
        { name: "X", link: "https://x.com/acraiaHQ", icon: IconBrandX },
        { name: "Discord", link: "https://discord.gg/acraia", icon: IconBrandDiscord },
        { name: "Github", link: "https://github.com/acraia-ai", icon: IconBrandGithub },
    ];
    return (
        <footer className="flex flex-col justify-between gap-4 border-t">
            <div className="flex flex-row items-center justify-between gap-4 py-4 px-6">
                <div className="flex items-center gap-4">
                    <Logo />
                    <p className="text-xs text-muted-foreground">
                        © Nolabs Tech 2025. All rights reserved.
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    {socialLinks.map((link) => (
                        <Link key={link.name} href={link.link}>
                            <Button variant={"ghost"} size={"icon"} className={"cursor-pointer rounded-full"}>
                                <link.icon />
                            </Button>
                        </Link>
                    ))}
                </div>
            </div>
        </footer>
    );
}