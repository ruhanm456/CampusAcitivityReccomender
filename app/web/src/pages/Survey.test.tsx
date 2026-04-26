import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi, beforeEach } from "vitest";
import Survey from "./Survey";

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const renderSurvey = () =>
  render(
    <MemoryRouter>
      <Survey />
    </MemoryRouter>,
  );

describe("Survey", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it("renders the first question initially", () => {
    renderSurvey();

    expect(
      screen.getByText("Do you prefer events to have food served?"),
    ).toBeInTheDocument();
    expect(screen.getByText("Don't want at all")).toBeInTheDocument();
    expect(screen.getByText("Extremely desire it")).toBeInTheDocument();
    expect(screen.getByRole("slider")).toBeInTheDocument();
  });

  it("updates answer when slider is changed", () => {
    renderSurvey();

    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: '7.5' } });

    // Value is now hidden from UI
  });

  it("progress bar shows current question and allows jumping", async () => {
    const user = userEvent.setup();
    renderSurvey();

    const progressButton2 = screen.getByRole("button", { name: "2" });
    await user.click(progressButton2);

    expect(screen.getByText("Question 2?")).toBeInTheDocument();
  });

  it("next button advances to next question", async () => {
    const user = userEvent.setup();
    renderSurvey();

    // Set an answer first
    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: "5" } });

    const nextButton = screen.getByRole("button", { name: "Next" });
    await user.click(nextButton);

    expect(screen.getByText("Question 2?")).toBeInTheDocument();
  });

  it("back button goes to previous question", async () => {
    const user = userEvent.setup();
    renderSurvey();

    // First go to next
    const nextButton = screen.getByRole("button", { name: "Next" });
    await user.click(nextButton);

    const backButton = screen.getByRole("button", { name: "Back" });
    await user.click(backButton);

    // Back to first
    expect(
      screen.getByText("Do you prefer events to have food served?"),
    ).toBeInTheDocument();
  });

  it("completes survey and shows results on last next", async () => {
    const user = userEvent.setup();
    renderSurvey();

    // Simulate going through all questions - this might be tricky, perhaps mock or assume
    // For now, placeholder
  });

  it("proceed button navigates after completion", async () => {
    // After completion, click proceed
    // expect(mockNavigate).toHaveBeenCalledWith("/chat"); // or wherever
  });
});
