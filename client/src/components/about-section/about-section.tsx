import { motion } from "framer-motion";
import Container from "@/components/container";
import ContentPadding from "@/components/content-padding";
import SectionHeader from "@/components/section-header";
import { LinkArrow } from "@/assets/icons";

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
  delay: 0.4,
};

const viewport = {
  once: true,
  amount: "some" as const,
};

const AboutSection = () => {
  return (
    <section
      id="about"
      className="mb-10 bg-dark py-12 md:mb-20 lg:mb-28 xl:mb-32 2xl:mb-36"
    >
      <Container>
        <div className="flex flex-col items-center justify-center gap-12">
          <SectionHeader
            titleText="About VQnA"
            subtitleText="Read about the benchmark, the model and the results."
            textTheme="light"
          />
          <ContentPadding>
            <div className="flex w-full flex-col items-center justify-center gap-4">
              <motion.p
                variants={variants}
                transition={transition}
                viewport={viewport}
                initial="initial"
                whileInView="animate"
                className="w-full text-start font-poppins text-xl font-light text-white"
              >
                NeuralVisions investigates visual question answering under the
                noisy, open-ended conditions represented by the VizWiz VQA
                benchmark. In contrast to conventional image classification, the
                task requires a model to interpret an image and a natural
                language question jointly, estimate whether the image contains
                enough information to support a valid response, and then map the
                pair to a short answer consistent with human annotations. The
                project is therefore centered on multimodal representation
                learning rather than on single-modality recognition alone.
                <br />
                <br />
                VizWiz is an especially meaningful benchmark because it comes
                from an assistive technology setting rather than from a tightly
                curated research workflow. The images are captured by blind
                users and paired with spoken questions about everyday objects,
                scenes, packaging, and text. As a result, the benchmark contains
                many images that are blurred, poorly framed, backlit, occluded,
                or otherwise difficult to interpret. Each example is paired with
                multiple human answers, and the benchmark explicitly evaluates
                both answer prediction and answerability prediction. This makes
                VizWiz a more realistic and substantially more difficult setting
                than many cleaner VQA datasets.
                <br />
                <br />
                The modeling direction used here is motivated by "Less Is More:
                Linear Layers on CLIP Features as Powerful VizWiz Model." The
                main claim of that work is that strong performance on VizWiz
                does not necessarily require a deep custom fusion stack or heavy
                end-to-end fine-tuning of a large vision-language model. A
                strong pretrained multimodal encoder can provide the bulk of the
                cross-modal representation, while shallow task-specific layers
                adapt those features to the answer space, answer type, and
                answerability objectives. This principle is the clearest
                conceptual basis for NeuralVisions.
                <br />
                <br />
                CLIP makes that simplification practical. Because CLIP is
                trained contrastively on large-scale image-text pairs, it embeds
                images and language into a shared space shaped by natural
                language supervision rather than by a closed taxonomy of labels.
                That property is especially useful for VizWiz, where a model may
                need to move between object recognition, scene understanding,
                color identification, and text-related reasoning in the same
                prediction pipeline. CLIP is not itself a visual question
                answering model, but it is a strong representation layer for the
                kind of noisy, multimodal understanding required here.
                <br />
                <br />
                NeuralVisions follows that recipe closely. The model uses the
                frozen CLIP ViT-L/14@336px image encoder together with CLIP's
                text encoder to generate feature vectors for the image and the
                tokenized question. These vectors are flattened, concatenated,
                normalized, and passed through a compact PyTorch head composed
                of dropout and linear layers. The primary branch predicts the
                answer over a fixed vocabulary of 5,410 answers. A second branch
                predicts one of four answer types: other, number, yes/no, and
                unanswerable. That answer-type prediction is expanded into a
                learnable gate over the answer vocabulary so the final answer
                logits can be biased toward more plausible regions of the label
                space.
                <br />
                <br />
                A third branch predicts answerability as a separate binary
                signal. During training, the model optimizes a multi-objective
                loss consisting of answer classification loss, answer-type
                classification loss, and binary cross-entropy loss for
                answerability. In effect, the model is encouraged to learn not
                only what answer is likely, but also what kind of answer should
                be expected and whether the image-question pair is answerable in
                the first place. This decomposition is important on VizWiz,
                where many errors arise from unanswerable or weakly grounded
                inputs rather than from ordinary class confusion alone.
                <br />
                <br />
                The archived training notebook helps explain why this structure
                is a good fit. The official VizWiz validation set is used for
                validation, while an additional held-out test split is derived
                from the official training data using stratification over answer
                type and answerability. Within that setup, the most common
                prompt by far is "What is this?", and the label distribution is
                heavily skewed toward other and unanswerable. Those properties
                help justify the auxiliary answer-type and answerability heads
                rather than treating the task as a single flat classification
                problem.
                <br />
                <br />
                In the archived CLIP-based experiment, the model reached 0.607
                VizWiz accuracy on validation, 0.672 VizWiz accuracy on the
                held-out test split, and 0.803 weighted average precision for
                answerability. For a design that keeps the CLIP backbone frozen
                and limits the learned task head to relatively shallow layers,
                these results support the central premise that representation
                quality and task decomposition can matter more than
                architectural depth alone. The model performs best when the
                pretrained embedding space already captures enough cross-modal
                structure for lightweight adaptation to succeed.
                <br />
                <br />
                The principal limitations of this approach follow directly from
                its simplicity. The answer space is fixed rather than
                generative, so the model cannot produce novel free-form answers
                outside the learned vocabulary. The shallow head also depends
                heavily on the quality of CLIP features and therefore inherits
                CLIP's strengths and weaknesses, including sensitivity to severe
                image degradation and imperfect handling of visually embedded
                text.
                <br />
                <br />
                Even so, NeuralVisions shows that a frozen multimodal encoder, a
                small amount of task-specific supervision, and a carefully
                structured objective can form a credible baseline for
                accessibility-oriented visual question answering.
              </motion.p>
              <hr className="h-px w-full border-none bg-muted" />
              <motion.div
                variants={variants}
                transition={transition}
                viewport={viewport}
                initial="initial"
                whileInView="animate"
                className="grid w-full grid-cols-2 gap-x-4 gap-y-2 lg:grid-cols-3 lg:gap-2"
              >
                <a
                  target="_blank"
                  href="/assets/files/Pattern Recognition - Visual Question Answering.pdf"
                  className="flex items-center justify-start gap-1 text-start font-poppins text-base font-light text-white underline lg:justify-center lg:text-center"
                >
                  Read our paper
                  <LinkArrow className="size-4 min-w-4 fill-white" />
                </a>
                <a
                  target="_blank"
                  href="https://www.kaggle.com/code/mohammadhelaly/visual-question-answering"
                  className="flex items-center justify-start gap-1 text-start font-poppins text-base font-light text-white underline lg:justify-center lg:text-center"
                >
                  Explore our notebook on Kaggle
                  <LinkArrow className="size-4 min-w-4 fill-white" />
                </a>
                <a
                  target="_blank"
                  href="https://openai.com/index/clip/"
                  className="flex items-center justify-start gap-1 text-start font-poppins text-base font-light text-white underline lg:justify-center lg:text-center"
                >
                  Read about CLIP
                  <LinkArrow className="size-4 min-w-4 fill-white" />
                </a>
                <a
                  target="_blank"
                  href="https://www.researchgate.net/publication/361274338_Less_Is_More_Linear_Layers_on_CLIP_Features_as_Powerful_VizWiz_Model"
                  className="flex items-center justify-start gap-1 text-start font-poppins text-base font-light text-white underline lg:justify-center lg:text-center"
                >
                  Read "Less is More"
                  <LinkArrow className="size-4 min-w-4 fill-white" />
                </a>
                <a
                  target="_blank"
                  href="https://huggingface.co/spaces/CVPR/VizWiz-CLIP-VQA/tree/main"
                  className="flex items-center justify-start gap-1 text-start font-poppins text-base font-light text-white underline lg:justify-center lg:text-center"
                >
                  Explore the code for "Less is More"
                  <LinkArrow className="size-4 min-w-4 fill-white" />
                </a>
                <a
                  target="_blank"
                  href="https://vizwiz.org/tasks-and-datasets/vqa/"
                  className="flex items-center justify-start gap-1 text-start font-poppins text-base font-light text-white underline lg:justify-center lg:text-center"
                >
                  Read about VizWiz VQA
                  <LinkArrow className="size-4 min-w-4 fill-white" />
                </a>
              </motion.div>
            </div>
          </ContentPadding>
        </div>
      </Container>
    </section>
  );
};

export default AboutSection;
