import { GitHub, Kaggle, OpenAi, VizWiz } from "@/assets/icons";
import Icon from "@/components/icon";

interface Props {
  variant?: "light" | "dark";
}

const Links = (props: Props) => {
  const { variant = "dark" } = props;

  const fillColor = variant === "light" ? "white" : "black";

  return (
    <div className="flex flex-row items-center justify-center gap-2 lg:gap-5">
      <Icon
        link="https://github.com/mohammadhelaly/neural-visions"
        name="GitHub"
      >
        <GitHub className={`size-8 rounded-sm fill-${fillColor}`} />
      </Icon>
      <Icon
        link="https://www.kaggle.com/code/mohammadhelaly/visual-question-answering"
        name="Kaggle"
      >
        <Kaggle className={`size-8 rounded-sm fill-${fillColor}`} />
      </Icon>
      <Icon link="https://openai.com/index/clip/" name="OpenAI">
        <OpenAi className={`size-8 rounded-sm fill-${fillColor}`} />
      </Icon>
      <Icon link="https://vizwiz.org/tasks-and-datasets/vqa/" name="VizWiz">
        <VizWiz className={`size-10 rounded-sm fill-${fillColor}`} />
      </Icon>
    </div>
  );
};

export default Links;
