# GCapricorn

*This data visualization project is completed for the BMI706 - Data Visualization for Biomedical Applications course.*

GCapricorn is an app that helps cancer researchers investigate cancer-related proteins.

Biomedical researchers, clinicians, and genetic counselors in the oncology field. Our application will allow researchers and clinicians to explore cancer-related proteins from the clinical level to the amino acid and nucleotide level.

Link to Streamlit app: https://kevinliu-bmb-bmi706-runtime-terror-gcapric-streamlit-app-t448c0.streamlit.app/

## Team Members

Team Runtime Terror
* Kevin Liu ([@kevinliu-bmb](https://github.com/kevinliu-bmb))
* Diego Trujillo ([@dietrujillo](https://github.com/dietrujillo))
* Michelle Theodory ([@mtheodory](https://github.com/mtheodory))

## Project Description
### View 1

View 1 will show a broad-level overview of all available cancer types, protein types, and associated characteristics. We will allow the user to select and filter a cancer type of interest or allow all cancer types with a drop-down menu. The main visualization is a grouped bar chart of protein classes per chromosome based on the Human Protein Atlas database [1], allowing the user to select one or multiple classes of proteins to display on the grouped bar chart. This will be done with a tooltip selector that filters by protein class. This view will also include a mouseover tooltip that allows a user to see specific protein count per protein class, by chromosome.

### View 2

In View 2, we intend to visualize the chromosomes and genes of interest corresponding to the selected cancer type. We will allow the user to use a dropdown selector to select the chromosome of interest and display the entire chromosome; subsequently, we will utilize a brush selector to allow the user to zoom into a particular chromosomal region of interest and provide a detailed view of proteins spanning the zoomed view of the chromosome. The detailed view of the brush-selected chromosomal region will display the respectively encoded proteins to the genes. Furthermore, the user will be provided with more details about the gene by hovering over the gene of interest; clicking the gene will direct the user to detailed protein-level descriptions and visualizations.

### View 3

Following the selection of the specific gene of interest, we will provide a detailed view of the selected protein. Specifically, we will allow the user to interact with a 3-dimensional interactive protein view (via JSmol)[2]. We will further provide a scrollable view of the corresponding amino acid sequence and associated protein properties; these details will be retrieved from the Gene Ontology (GO) [3] and UniProt databases [4]. We will also show a comparison bar chart of the cancer risk score with similar proteins that the researcher might also want to explore. The bars on this bar chart will be clickable elements, and when clicked will select the similar protein. This will allow researchers to quickly go through proteins of interest without having to find them in the explorer. 

## References
    
    [1] The Human Protein Atlas: Data from the Human Protein Atlas in tab-separated format. https://proteinatlas.org

    [2] JSmol: an open-source HTML5 viewer for chemical structures in 3D. http://wiki.jmol.org/index.php/JSmol

    [3] Ashburner et al. Gene ontology: tool for the unification of biology. Nat Genet. May 2000;25(1):25-9.

    [4] The UniProt Consortium, UniProt: the Universal Protein Knowledgebase in 2023, Nucleic Acids Res. 51:D523–D531 (2023)
