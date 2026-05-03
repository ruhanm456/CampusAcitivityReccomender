import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import ChatWindow from "../pages/ChatWindow";

const renderChatWindow = () =>
  render(
    <MemoryRouter>
      <ChatWindow />
    </MemoryRouter>
  );

describe("ChatWindow", () => {
  it("renders the header and empty state prompts", () => {
    renderChatWindow();

    expect(
      screen.getByRole("heading", { name: "Campus Chat" })
    ).toBeInTheDocument();
    expect(screen.getByText("Ask about campus life...")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "What clubs are active this week?" })
    ).toBeInTheDocument();
  });

  it("fills the input when a suggestion is clicked", async () => {
    const user = userEvent.setup();
    renderChatWindow();

    const suggestion = screen.getByRole("button", {
      name: "Find study groups for CS classes",
    });

    await user.click(suggestion);

    expect(screen.getByLabelText("Message")).toHaveValue(
      "Find study groups for CS classes"
    );
  });

  it("sends a message and clears the input", async () => {
    const user = userEvent.setup();
    renderChatWindow();

    const input = screen.getByLabelText("Message");
    const sendButton = screen.getByRole("button", { name: "Send" });

    expect(sendButton).toBeDisabled();

    await user.type(input, "Hello there!");
    expect(sendButton).toBeEnabled();

    await user.click(sendButton);

    expect(input).toHaveValue("");
    expect(screen.getByText("Hello there!")).toBeInTheDocument();
  });

  it("shows typing feedback before the assistant response", async () => {
    vi.useFakeTimers();
    const user = userEvent.setup({
      advanceTimers: vi.advanceTimersByTime.bind(vi),
    });
    renderChatWindow();

    const input = screen.getByLabelText("Message");
    await user.type(input, "Any events?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(screen.getByText("Typing...")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(600);
    });

    expect(
      screen.getByText(
        "Thanks for the question! I can help you find campus activities."
      )
    ).toBeInTheDocument();

    vi.useRealTimers();
  });
});
