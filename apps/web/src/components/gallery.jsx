import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "./ui/card";
import { agents } from "@/data/agents";
import { Button } from "./ui/button";
import Link from "next/link";
import Image from "next/image";
export default function Gallery() {
    return (
        <div className="grid grid-cols-1 my-4 mx-6 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {agents.map((agent) => (
                <Card key={agent.slug} className="pt-0 overflow-hidden">
                    <Image src={agent.thumbnail} alt={agent.name} className="w-full h-56 object-cover" width={1000} height={1000} />
                    <CardHeader className="">
                        <CardTitle>{agent.name}</CardTitle>
                        <CardDescription>{agent.description}</CardDescription>
                    </CardHeader> 
                    <CardContent>
                        <p>{agent.description}</p>
                    </CardContent>
                    <CardFooter>
                        <Link href={`/agent/${agent.slug}`}>
                            <Button className={"cursor-pointer rounded-full"} variant={"outline"}>
                                Checkout
                            </Button>
                        </Link>
                    </CardFooter>
                </Card>
            ))}
        </div>
    );
}