import { motion } from "framer-motion";
import Container from "@/components/container";
import Links from "@/components/links";

const variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
  },
};

const transition = {
  type: "tween",
  duration: 0.4,
  staggerChildren: 0.2,
};

const viewport = {
  once: true,
  amount: "all" as const,
};

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="footer" className="bg-dark py-12">
      <Container>
        <motion.div
          variants={variants}
          transition={transition}
          viewport={viewport}
          initial="initial"
          whileInView="animate"
          className="flex w-full flex-col items-center justify-center gap-4 lg:items-start"
        >
          <motion.div
            variants={variants}
            transition={transition}
            className="flex w-full flex-col items-center justify-center gap-4 lg:flex-row lg:items-end lg:justify-between lg:px-2"
          >
            <div className="flex flex-col items-center gap-1.5 lg:items-start">
              <p className="text-center font-poppins text-xs font-thin text-white lg:text-start">
                Background by{" "}
                <a
                  href="https://objkt.com/@xponential"
                  target="_blank"
                  rel="noreferrer"
                  className="text-white underline"
                >
                  xponentialdesign
                </a>
                .
              </p>
              <p className="text-center font-poppins text-xs font-thin text-white lg:text-start">
                Neural network deep learning model developed with{" "}
                <a
                  href="https://pytorch.org/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-white underline"
                >
                  PyTorch
                </a>
                .
              </p>
              <p className="text-center font-poppins text-xs font-thin text-white lg:text-start">
                Deep learning model incorporates the{" "}
                <a
                  href="https://openai.com/index/clip/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-white underline"
                >
                  OpenAI CLIP encoder
                </a>
                .
              </p>
              <p className="text-center font-poppins text-xs font-thin text-white lg:text-start">
                Model trained on the{" "}
                <a
                  href="https://vizwiz.org/tasks-and-datasets/vqa/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-white underline"
                >
                  VizWiz VQA dataset
                </a>
                .
              </p>
              <p className="text-center font-poppins text-xs font-thin text-white lg:text-start">
                Backend server developed with{" "}
                <a
                  href="https://flask.palletsprojects.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-white underline"
                >
                  Flask
                </a>
                .
              </p>
              <p className="text-center font-poppins text-xs font-thin text-white lg:text-start">
                Developed with{" "}
                <a
                  href="https://react.dev/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-white underline"
                >
                  React.js
                </a>
                .
              </p>
            </div>
            <Links variant="light" />
          </motion.div>
          <hr className="h-px w-full border-none !bg-muted" />
          <motion.p
            variants={variants}
            transition={transition}
            className="text-center font-poppins text-xs font-thin text-white lg:px-2 lg:text-start"
          >
            &copy; {currentYear} Mohammad Helaly
          </motion.p>
        </motion.div>
      </Container>
    </footer>
  );
};

export default Footer;
