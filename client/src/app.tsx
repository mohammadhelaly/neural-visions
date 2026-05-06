import NavBar from "@/components/nav-bar";
import Background from "@/components/background";
import HomeSection from "@/components/home-section";
import VQnASection from "@/components/vqna-section";
import AboutSection from "@/components/about-section";
import ContactSection from "@/components/contact-section";
import Footer from "@/components/footer";

const App = () => {
  return (
    <>
      <NavBar />
      <main>
        <Background />
        <HomeSection />
        <VQnASection />
        <AboutSection />
        <ContactSection />
      </main>
      <Footer />
    </>
  );
};

export default App;
