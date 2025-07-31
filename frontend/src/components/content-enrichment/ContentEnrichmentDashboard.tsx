import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  FileText,
  BarChart3,
  TrendingUp,
  Target,
  Zap,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';

interface ProductData {
  id: string;
  title?: string;
  description?: string;
  price?: number;
  category?: string;
  brand?: string;
  sku?: string;
  attributes?: Record<string, any>;
  images?: string[];
}

interface EnrichmentResult {
  product_id: string;
  enrichment_score: number;
  applied_enrichments: string[];
  quality_metrics: Record<string, number>;
  suggestions: string[];
  enriched_product: ProductData;
}

interface AnalyticsData {
  total_products: number;
  content_quality_scores: {
    average: number;
    distribution: Record<string, number>;
  };
  seo_performance: {
    average: number;
    distribution: Record<string, number>;
  };
  completeness_analysis: {
    average: number;
    distribution: Record<string, number>;
  };
  recommendations: string[];
}

const ContentEnrichmentDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [products, setProducts] = useState<ProductData[]>([]);
  const [enrichmentResults, setEnrichmentResults] = useState<EnrichmentResult[]>([]);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [selectedEnrichments, setSelectedEnrichments] = useState<string[]>([
    'seo_optimization',
    'content_generation'
  ]);

  const enrichmentTypes = [
    { id: 'seo_optimization', label: 'SEO Optimization', icon: Target },
    { id: 'content_generation', label: 'Content Generation', icon: FileText },
    { id: 'amazon_optimization', label: 'Amazon Optimization', icon: Zap },
    { id: 'quality_scoring', label: 'Quality Scoring', icon: BarChart3 },
    { id: 'categorization', label: 'Auto Categorization', icon: Info }
  ];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = file.name.endsWith('.xml')
        ? '/api/content-enrichment/upload/xml'
        : '/api/content-enrichment/upload/csv';

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      setProducts(result.products);
      setActiveTab('products');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEnrichProducts = async () => {
    if (products.length === 0) return;

    setIsProcessing(true);

    try {
      const response = await fetch('/api/content-enrichment/enrich/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          products: products,
          config: {
            enabled_types: selectedEnrichments,
            target_channels: ['website', 'amazon'],
            languages: ['en']
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Enrichment failed');
      }

      const result = await response.json();
      setEnrichmentResults(result.results);
      setActiveTab('results');
    } catch (error) {
      console.error('Enrichment error:', error);
      alert('Enrichment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAnalyzeContent = async () => {
    if (products.length === 0) return;

    try {
      const response = await fetch('/api/content-enrichment/analytics/content-performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(products),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      setAnalyticsData(result);
      setActiveTab('analytics');
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis failed. Please try again.');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return 'default';
    if (score >= 60) return 'secondary';
    return 'destructive';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Content Enrichment & Analytics Platform</h1>
          <p className="text-muted-foreground">
            Optimize your product content with AI-powered enrichment and analytics
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <FileText className="w-4 h-4" />
            {products.length} Products
          </Badge>
          {enrichmentResults.length > 0 && (
            <Badge variant="outline" className="flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              {enrichmentResults.length} Enriched
            </Badge>
          )}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="upload">Upload Data</TabsTrigger>
          <TabsTrigger value="products">Products</TabsTrigger>
          <TabsTrigger value="enrich">Enrich</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Upload Product Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <div className="space-y-2">
                  <p className="text-lg font-medium">Upload your product data</p>
                  <p className="text-sm text-muted-foreground">
                    Supports XML and CSV formats. Maximum file size: 50MB
                  </p>
                </div>
                <div className="mt-4">
                  <Input
                    type="file"
                    accept=".xml,.csv"
                    onChange={handleFileUpload}
                    disabled={isProcessing}
                    className="max-w-xs mx-auto"
                  />
                </div>
                {isProcessing && (
                  <div className="mt-4">
                    <Progress value={undefined} className="w-full max-w-xs mx-auto" />
                    <p className="text-sm text-muted-foreground mt-2">Processing file...</p>
                  </div>
                )}
              </div>

              {uploadedFile && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Uploaded: {uploadedFile.name} ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="products" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Product Data ({products.length} items)
                </span>
                <div className="flex gap-2">
                  <Button onClick={handleAnalyzeContent} variant="outline">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    Analyze
                  </Button>
                  <Button onClick={() => setActiveTab('enrich')}>
                    <Zap className="w-4 h-4 mr-2" />
                    Enrich Content
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {products.slice(0, 10).map((product) => (
                  <div key={product.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2 flex-1">
                        <h3 className="font-medium">{product.title || `Product ${product.id}`}</h3>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {product.description || 'No description available'}
                        </p>
                        <div className="flex gap-2 flex-wrap">
                          {product.category && (
                            <Badge variant="secondary">{product.category}</Badge>
                          )}
                          {product.brand && (
                            <Badge variant="outline">{product.brand}</Badge>
                          )}
                          {product.price && (
                            <Badge variant="outline">${product.price}</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {products.length > 10 && (
                  <p className="text-sm text-muted-foreground text-center">
                    ... and {products.length - 10} more products
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="enrich" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Content Enrichment Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-base font-medium">Select Enrichment Types</Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
                  {enrichmentTypes.map((type) => {
                    const Icon = type.icon;
                    const isSelected = selectedEnrichments.includes(type.id);
                    return (
                      <div
                        key={type.id}
                        className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                          isSelected
                            ? 'border-primary bg-primary/5'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => {
                          if (isSelected) {
                            setSelectedEnrichments(prev => prev.filter(id => id !== type.id));
                          } else {
                            setSelectedEnrichments(prev => [...prev, type.id]);
                          }
                        }}
                      >
                        <div className="flex items-center gap-2">
                          <Icon className="w-4 h-4" />
                          <span className="text-sm font-medium">{type.label}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex justify-center pt-4">
                <Button
                  onClick={handleEnrichProducts}
                  disabled={isProcessing || products.length === 0 || selectedEnrichments.length === 0}
                  size="lg"
                >
                  {isProcessing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Enriching Products...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Enrich {products.length} Products
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Enrichment Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              {enrichmentResults.length === 0 ? (
                <div className="text-center py-8">
                  <AlertCircle className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-lg font-medium">No enrichment results yet</p>
                  <p className="text-sm text-muted-foreground">
                    Upload products and run enrichment to see results here
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {enrichmentResults.map((result) => (
                    <div key={result.product_id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="font-medium">
                          {result.enriched_product.title || `Product ${result.product_id}`}
                        </h3>
                        <Badge
                          variant={getScoreBadgeVariant(result.enrichment_score)}
                          className="ml-2"
                        >
                          Score: {result.enrichment_score.toFixed(1)}
                        </Badge>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <Label className="text-sm font-medium">Applied Enrichments</Label>
                          <div className="flex gap-1 flex-wrap mt-1">
                            {result.applied_enrichments.map((enrichment) => (
                              <Badge key={enrichment} variant="outline" className="text-xs">
                                {enrichment.replace('_', ' ')}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        {result.suggestions.length > 0 && (
                          <div>
                            <Label className="text-sm font-medium">Suggestions</Label>
                            <ul className="text-sm text-muted-foreground mt-1 space-y-1">
                              {result.suggestions.slice(0, 3).map((suggestion, index) => (
                                <li key={index} className="flex items-start gap-2">
                                  <span className="text-primary">•</span>
                                  <span>{suggestion}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
                          {Object.entries(result.quality_metrics).map(([metric, value]) => (
                            <div key={metric} className="text-center">
                              <div className={`text-lg font-semibold ${getScoreColor(value as number)}`}>
                                {typeof value === 'number' ? value.toFixed(1) : value}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {metric.replace('_', ' ')}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Content Quality</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData?.content_quality_scores.average.toFixed(1) || '0'}
                </div>
                <p className="text-xs text-muted-foreground">Average score</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">SEO Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData?.seo_performance.average.toFixed(1) || '0'}
                </div>
                <p className="text-xs text-muted-foreground">Average score</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Completeness</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData?.completeness_analysis.average.toFixed(1) || '0'}
                </div>
                <p className="text-xs text-muted-foreground">Average score</p>
              </CardContent>
            </Card>
          </div>

          {analyticsData && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {analyticsData.recommendations.map((recommendation, index) => (
                    <Alert key={index}>
                      <Info className="h-4 w-4" />
                      <AlertDescription>{recommendation}</AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContentEnrichmentDashboard;
