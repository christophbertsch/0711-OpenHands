/* eslint-disable i18next/no-literal-string */
import React, { useState, useCallback } from "react";

interface Product {
  id: string;
  title: string;
  description: string;
  price?: number;
  category?: string;
  brand?: string;
  sku?: string;
  attributes?: Record<string, unknown>;
  images?: string[];
}

interface EnrichmentResult {
  status: string;
  original_product: Product;
  enriched_product: Product;
  enrichment_score: number;
  applied_enrichments: string[];
  suggestions: string[];
  quality_metrics?: Record<string, number>;
}

interface AnalyticsData {
  total_products: number;
  content_quality_scores: {
    average: number;
    distribution: Record<string, number>;
  };
  seo_performance: {
    average: number;
  };
  completeness_analysis: {
    average: number;
  };
  recommendations: string[];
}

function ContentEnrichmentDashboard() {
  const [activeTab, setActiveTab] = useState<"upload" | "enrich" | "analytics">(
    "upload",
  );
  const [products, setProducts] = useState<Product[]>([]);
  const [enrichmentResults, setEnrichmentResults] = useState<
    EnrichmentResult[]
  >([]);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      setIsLoading(true);
      setError(null);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const endpoint = file.name.endsWith(".xml")
          ? "/api/content-enrichment/upload/xml"
          : "/api/content-enrichment/upload/csv";

        const response = await fetch(endpoint, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();
        setProducts(result.products || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const handleEnrichProducts = useCallback(async () => {
    if (products.length === 0) return;

    setIsLoading(true);
    setError(null);

    try {
      const enrichmentConfig = {
        enabled_types: [
          "seo_optimization",
          "content_generation",
          "amazon_optimization",
        ],
        target_channels: ["website", "amazon"],
        languages: ["en"],
        seo_keywords: ["premium", "quality", "professional"],
      };

      const response = await fetch("/api/content-enrichment/enrich/batch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          products: products.slice(0, 5), // Limit to first 5 for demo
          config: enrichmentConfig,
        }),
      });

      if (!response.ok) {
        throw new Error(`Enrichment failed: ${response.statusText}`);
      }

      const result = await response.json();
      setEnrichmentResults(result.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Enrichment failed");
    } finally {
      setIsLoading(false);
    }
  }, [products]);

  const handleAnalyzeContent = useCallback(async () => {
    if (products.length === 0) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        "/api/content-enrichment/analytics/content-performance",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(products),
        },
      );

      if (!response.ok) {
        throw new Error(`Analytics failed: ${response.statusText}`);
      }

      const result = await response.json();
      setAnalyticsData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analytics failed");
    } finally {
      setIsLoading(false);
    }
  }, [products]);

  const renderUploadTab = () => (
    <div className="space-y-6">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <div className="space-y-4">
          <div className="text-4xl">📁</div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Upload Product Data
            </h3>
            <p className="text-gray-500">Support for XML and CSV files</p>
          </div>
          <input
            type="file"
            accept=".xml,.csv"
            onChange={handleFileUpload}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            disabled={isLoading}
          />
        </div>
      </div>

      {products.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Uploaded Products ({products.length})
          </h3>
          <div className="space-y-3">
            {products.slice(0, 3).map((product) => (
              <div key={product.id} className="border rounded p-3">
                <div className="font-medium">{product.title}</div>
                <div className="text-sm text-gray-500">
                  {product.category} • ${product.price}
                </div>
              </div>
            ))}
            {products.length > 3 && (
              <div className="text-sm text-gray-500">
                ... and {products.length - 3} more products
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderEnrichmentTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Content Enrichment
        </h3>
        <button
          type="button"
          onClick={handleEnrichProducts}
          disabled={isLoading || products.length === 0}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Enriching..." : "Enrich Products"}
        </button>
      </div>

      {enrichmentResults.length > 0 && (
        <div className="space-y-4">
          {enrichmentResults.map((result, index) => (
            <div key={index} className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="font-medium">
                    {result.original_product.title}
                  </h4>
                  <p className="text-sm text-gray-500">
                    ID: {result.original_product.id}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {result.enrichment_score.toFixed(1)}
                  </div>
                  <div className="text-sm text-gray-500">Score</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Original</h5>
                  <div className="text-sm text-gray-600">
                    <p>
                      <strong>Title:</strong> {result.original_product.title}
                    </p>
                    <p>
                      <strong>Description:</strong>{" "}
                      {result.original_product.description?.substring(0, 100)}
                      ...
                    </p>
                  </div>
                </div>
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Enriched</h5>
                  <div className="text-sm text-gray-600">
                    <p>
                      <strong>Title:</strong> {result.enriched_product.title}
                    </p>
                    <p>
                      <strong>Description:</strong>{" "}
                      {result.enriched_product.description?.substring(0, 100)}
                      ...
                    </p>
                  </div>
                </div>
              </div>

              {result.applied_enrichments.length > 0 && (
                <div className="mt-4">
                  <h5 className="font-medium text-gray-900 mb-2">
                    Applied Enrichments
                  </h5>
                  <div className="flex flex-wrap gap-2">
                    {result.applied_enrichments.map((enrichment, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {enrichment}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {result.suggestions.length > 0 && (
                <div className="mt-4">
                  <h5 className="font-medium text-gray-900 mb-2">
                    Suggestions
                  </h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {result.suggestions.slice(0, 3).map((suggestion, i) => (
                      <li key={i}>• {suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Analytics Dashboard
        </h3>
        <button
          type="button"
          onClick={handleAnalyzeContent}
          disabled={isLoading || products.length === 0}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Analyzing..." : "Analyze Content"}
        </button>
      </div>

      {analyticsData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-2xl font-bold text-blue-600">
              {analyticsData.total_products}
            </div>
            <div className="text-sm text-gray-500">Total Products</div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-2xl font-bold text-green-600">
              {analyticsData.content_quality_scores.average.toFixed(1)}
            </div>
            <div className="text-sm text-gray-500">Avg Quality Score</div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-2xl font-bold text-purple-600">
              {analyticsData.seo_performance.average.toFixed(1)}
            </div>
            <div className="text-sm text-gray-500">Avg SEO Score</div>
          </div>
        </div>
      )}

      {analyticsData?.recommendations &&
        analyticsData.recommendations.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <h4 className="font-medium text-gray-900 mb-4">Recommendations</h4>
            <ul className="space-y-2">
              {analyticsData.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-yellow-500 mr-2">💡</span>
                  <span className="text-sm text-gray-600">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Content Enrichment & Analytics
          </h1>
          <p className="text-gray-600 mt-2">
            AI-powered content optimization for e-commerce and product data
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-red-800">{error}</div>
          </div>
        )}

        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { id: "upload", label: "Upload Data", icon: "📁" },
                { id: "enrich", label: "Enrich Content", icon: "🚀" },
                { id: "analytics", label: "Analytics", icon: "📊" },
              ].map((tab) => (
                <button
                  type="button"
                  key={tab.id}
                  onClick={() =>
                    setActiveTab(tab.id as "upload" | "enrich" | "analytics")
                  }
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === "upload" && renderUploadTab()}
            {activeTab === "enrich" && renderEnrichmentTab()}
            {activeTab === "analytics" && renderAnalyticsTab()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContentEnrichmentDashboard;
