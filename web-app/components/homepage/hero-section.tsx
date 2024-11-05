"use client"
import { ArrowRight, Github } from 'lucide-react';
import Link from "next/link";
import { BorderBeam } from "../magicui/border-beam";
import { Button } from "../ui/button";
export default function HeroSection() {

    return (
        <div className='flex flex-col items-center justify-center leading-6 mt-[3rem]'>
            {/* <div className="my-5"
                <AnimatedGradientTextComponent />
            </div> */}
            <h1 className="scroll-m-20 text-4xl sm:text-4xl md:text-6xl font-semibold tracking-tight lg:text-7xl text-center max-w-[1120px] bg-gradient-to-b dark:text-white">
                AI Texas Hold'em Poker
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-500 text-xl text-center mt-2 dark:text-gray-400">
                Your best AI tools for Texas Hold'em Pokers
            </p>
            <div className="flex justify-center items-center gap-3">
                <Link href="/play" className="mt-5">
                    <Button className="animate-buttonheartbeat rounded-md bg-blue-600 hover:bg-blue-500 text-sm font-semibold text-white">Get Started</Button>
                </Link>
                <Link href="https://discord.com/invite/N3kad5yx9J" target='_blank' className="mt-5">
                    <Button variant="outline" className="flex gap-1 ">Join Discord<ArrowRight className='w-4 h-4' /></Button>
                </Link>
            </div>
            <div>
                <div className="relative flex max-w-6xl justify-center overflow-hidden mt-7">
                    <div className="relative rounded-xl">
                        <img
                            src="https://i0.wp.com/www.sciencenews.org/wp-content/uploads/2019/07/071019_MT_poker-ai_feat.jpg?fit=860%2C460&ssl=1"
                            alt="Hero Image"
                            className="block w-[1200px] rounded-[inherit] border object-contain shadow-lg dark:hidden"
                        />
                        <img
                            src="https://i0.wp.com/www.sciencenews.org/wp-content/uploads/2019/07/071019_MT_poker-ai_feat.jpg?fit=860%2C460&ssl=1"
                            alt="Hero Image"
                            className="dark:block w-[1200px] rounded-[inherit] border object-contain shadow-lg hidden"
                        />
                        <BorderBeam size={250} duration={12} delay={9} />
                    </div>
                </div>
            </div>

        </div>
    )
}