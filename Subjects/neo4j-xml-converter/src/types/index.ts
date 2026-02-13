export interface NodeData {
    id: string;
    labels: string[];
    properties: Record<string, any>;
}

export interface XmlData {
    subjectId: string;
    preferredTerm: string;
    nonPreferredTerms: string[];
    coordinates: {
        latitude: number;
        longitude: number;
    };
    placeTypes: string[];
}