import * as fs from 'fs';
import * as xml2js from 'xml2js';
import { XmlData } from '../types';

export class XmlParser {
    private parser: xml2js.Parser;

    constructor() {
        this.parser = new xml2js.Parser();
    }

    public parseXml(filePath: string): Promise<XmlData> {
        return new Promise((resolve, reject) => {
            fs.readFile(filePath, (err, data) => {
                if (err) {
                    return reject(err);
                }
                this.parser.parseString(data, (err, result) => {
                    if (err) {
                        return reject(err);
                    }
                    resolve(result);
                });
            });
        });
    }

    public extractData(parsedXml: any): any {
        const subject = parsedXml.Vocabulary.Subject;
        const terms = subject[0].Terms[0];
        const placeTypes = subject[0].Place_Types[0];

        const extractedData = {
            subjectId: subject[0].$.Subject_ID,
            preferredTerm: terms.Preferred_Term[0].Term_Text[0],
            nonPreferredTerms: terms['Non-Preferred_Term'].map((term: any) => term.Term_Text[0]),
            placeTypes: placeTypes.Preferred_Place_Type.map((type: any) => type.Place_Type_ID[0]),
            coordinates: {
                latitude: subject[0].Coordinates[0].Standard[0].Latitude[0].Decimal[0],
                longitude: subject[0].Coordinates[0].Standard[0].Longitude[0].Decimal[0],
            },
        };

        return extractedData;
    }
}