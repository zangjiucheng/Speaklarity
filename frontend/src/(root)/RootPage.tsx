import {LineShadowText} from '../components/magicui/line-shadow-text.tsx';
import {AnimatedGridPattern} from '../components/magicui/animated-grid-pattern.tsx';
import {InteractiveHoverButton} from '../components/magicui/interactive-hover-button.tsx';


export const RootPage = () => {
    return (
        <div className="relative w-screen h-screen flex flex-col items-center justify-center overflow-hidden">
            <AnimatedGridPattern
                numSquares={60}
                maxOpacity={0.8}
                duration={2}
                repeatDelay={0.2}
                speed={5000}
                className={'inset-x-0 inset-y-[-30%] h-[200%] -skew-y-8 overflow-hidden blur-2xl'}
            />
            <div className={'flex flex-col items-center justify-center py-8'}>
                <img src="/icon.png" alt="Speaklarity" className="mb-5"/>
                <LineShadowText className={'text-6xl mb-8 font-semibold'}>Speaklarity</LineShadowText>
                <h3 className="text-2xl my-8 opacity-70 font-semibold">Speak clearly, be heard confidently.</h3>
                <p className={'text-xl w-[70vw] max-w-[800px] text-center opacity-70 italic mb-8'}>
                    Speaklarity is an AI-powered accent correction app that helps you improve pronunciation and
                    fluency
                    through personalized feedback and guided practice.
                </p>
                <div>
                    <InteractiveHoverButton className="drop-shadow">
                        Get Started
                    </InteractiveHoverButton>
                </div>
            </div>
        
        </div>
    );
};