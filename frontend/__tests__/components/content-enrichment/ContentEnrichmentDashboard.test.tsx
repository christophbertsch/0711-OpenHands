import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ContentEnrichmentDashboard from "../../../src/components/content-enrichment/ContentEnrichmentDashboard";

describe("ContentEnrichmentDashboard", () => {
  it("renders the main heading", () => {
    render(<ContentEnrichmentDashboard />);
    
    expect(
      screen.getByText("Content Enrichment & Analytics")
    ).toBeInTheDocument();
  });

  it("renders the upload tab by default", () => {
    render(<ContentEnrichmentDashboard />);
    
    expect(screen.getByText("Upload Product Data")).toBeInTheDocument();
    expect(screen.getByText("Support for XML and CSV files")).toBeInTheDocument();
  });

  it("renders all navigation tabs", () => {
    render(<ContentEnrichmentDashboard />);
    
    expect(screen.getByText("Upload Data")).toBeInTheDocument();
    expect(screen.getByText("Enrich Content")).toBeInTheDocument();
    expect(screen.getByText("Analytics")).toBeInTheDocument();
  });

  it("renders file input for uploads", () => {
    render(<ContentEnrichmentDashboard />);
    
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute("accept", ".xml,.csv");
  });
});