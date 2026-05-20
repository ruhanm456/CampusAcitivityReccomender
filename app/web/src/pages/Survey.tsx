import { useState } from "react";
import { useNavigate } from "react-router-dom";

interface Question {
  question: string;
  minLabel: string;
  maxLabel: string;
  isFloat: boolean;
}

const questions: Question[] = [
  {
    question: "Do you prefer events to have food served?",
    minLabel: "Don't want at all",
    maxLabel: "Extremely desire it",
    isFloat: false,
  },
  // Add placeholders for the rest
  ...Array.from({ length: 19 }, (_, i) => ({
    question: `Question ${i + 2}?`,
    minLabel: "Min",
    maxLabel: "Max",
    isFloat: false,
  })),
];

const Survey: React.FC = () => {
  const navigate = useNavigate();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>(
    new Array(questions.length).fill(null),
  );
  const [isCompleted, setIsCompleted] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];
  const currentAnswer = answers[currentQuestionIndex];

  const handleSliderChange = (value: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestionIndex] = value;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      setIsCompleted(true);
    }
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleProgressClick = (index: number) => {
    setCurrentQuestionIndex(index);
  };

  const handleProceed = () => {
    navigate("/chat"); // Placeholder
  };

  if (isCompleted) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Survey Results</h1>
        <div className="space-y-4">
          {questions.map((q, i) => (
            <div key={i} className="card bg-base-100 shadow-md p-4">
              <p className="font-semibold">{q.question}</p>
              <p>Answer: {answers[i] ?? "Not answered"}</p>
            </div>
          ))}
        </div>
        <button className="btn btn-primary mt-4" onClick={handleProceed}>
          Proceed
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">User Preferences Survey</h1>

      {/* Progress Bar */}
      <div className="flex flex-wrap gap-2 mb-6">
        {questions.map((_, i) => (
          <button
            key={i}
            className={`btn btn-sm ${
              i === currentQuestionIndex ? "btn-primary" : "btn-outline"
            }`}
            onClick={() => handleProgressClick(i)}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {/* Question */}
      <div className="card bg-base-100 shadow-md p-6">
        <h2 className="text-xl mb-4">{currentQuestion.question}</h2>

        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{currentQuestion.minLabel}</span>
          <span>{currentQuestion.maxLabel}</span>
        </div>

        <input
          type="range"
          min="1"
          max="10"
          step="0.1"
          value={currentAnswer ?? 5}
          onChange={(e) => handleSliderChange(Number(e.target.value))}
          className="range range-primary w-full"
          role="slider"
        />
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <button
          className="btn btn-outline"
          onClick={handleBack}
          disabled={currentQuestionIndex === 0}
        >
          Back
        </button>
        <button
          className="btn btn-primary"
          onClick={handleNext}
          disabled={currentAnswer === null}
        >
          {currentQuestionIndex === questions.length - 1 ? "Complete" : "Next"}
        </button>
      </div>
    </div>
  );
};

export default Survey;
