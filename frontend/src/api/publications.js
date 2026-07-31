import api from "./axios";


// ============================================================
// MY PUBLICATIONS
// ============================================================

export async function getMyPublications() {

  const response = await api.get(
    "/publications"
  );

  return response.data;
}


export async function createPublication(
  publication
) {

  const response = await api.post(
    "/publications",
    publication
  );

  return response.data;
}


export async function updatePublication(
  publicationId,
  publication
) {

  const response = await api.patch(
    `/publications/${publicationId}`,
    publication
  );

  return response.data;
}


export async function deletePublication(
  publicationId
) {

  const response = await api.delete(
    `/publications/${publicationId}`
  );

  return response.data;
}


// ============================================================
// OPENALEX DISCOVERY
// ============================================================

export async function importOpenAlexPublications(
  query,
  limit
) {

  const response = await api.post(
    "/publications/import/openalex",
    null,
    {
      params: {
        query,
        limit,
      },
    }
  );

  return response.data;
}


// ============================================================
// RESEARCH LIBRARY
// ============================================================

export async function getResearchLibrary() {

  const response = await api.get(
    "/publications/library/imported"
  );

  return response.data;
}


export async function removeFromResearchLibrary(
  publicationId
) {

  const response = await api.delete(
    `/publications/library/${publicationId}`
  );

  return response.data;
}


// ============================================================
// AI RECOMMENDATIONS
// ============================================================

export async function getPublicationRecommendations() {

  const response = await api.get(
    "/publications/recommendations/ai"
  );

  return response.data;
}


// ============================================================
// UPLOAD PUBLICATION PDF
// ============================================================

export async function uploadPublicationPdf(
  publicationId,
  file
) {

  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  const response = await api.post(
    `/publications/${publicationId}/pdf`,
    formData
  );

  return response.data;
}


// ============================================================
// VIEW PUBLICATION PDF
// ============================================================

export async function viewPublicationPdf(
  publicationId
) {

  const response = await api.get(
    `/publications/${publicationId}/pdf`,
    {
      responseType: "blob",
    }
  );


  const pdfBlob =
    new Blob(
      [response.data],
      {
        type: "application/pdf",
      }
    );


  const pdfUrl =
    window.URL.createObjectURL(
      pdfBlob
    );


  window.open(
    pdfUrl,
    "_blank"
  );


  // Keep URL alive long enough for the
  // browser tab to load the PDF.

  setTimeout(() => {

    window.URL.revokeObjectURL(
      pdfUrl
    );

  }, 60000);
}