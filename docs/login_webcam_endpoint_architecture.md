# /api/login/webcam endpoint architecture

> This is an “architecture image” using Mermaid (renders in VS Code + GitHub).

## High-level flow (components)

```mermaid
flowchart TD
  Client["Client (Postman)"] -->|"POST /api/login/webcam\nform-data: file=<image>"| LoginAPI["Auth API: /api/login/webcam"]

  LoginAPI -->|"delegates"| WebcamAuth["router.webcam_auth (shared)\nPOST /auth/webcam"]

  WebcamAuth --> FaceSvc["face_auth.authenticate_face()"]
  FaceSvc --> Detect["OpenCV Haar Cascade\nhaarcascade_frontalface_default.xml"]

  Detect -->|"face found"| Token["Generate token (secrets.token_urlsafe)\nAdd to in-memory set"]
  Detect -->|"no face"| Deny["401 Unauthorized\nNo face detected"]

  Token -->|"{ authenticated: true, token }"| Client
  Deny -->|"error response"| Client
```

## Runtime sequence (per request)

```mermaid
sequenceDiagram
  autonumber
  participant C as Client
  participant A as /api/login/webcam
  participant R as router.webcam_auth
  participant F as authenticate_face
  participant CV as OpenCV detect_face_from_image
  participant T as Token store (in-memory set)

  C->>A: POST /api/login/webcam (UploadFile image)
  A->>R: call webcam_auth(file)
  R->>F: await authenticate_face(file)
  F-->>R: true/false

  alt Face detected
    R->>CV: detectMultiScale(...) (Haar cascade)
    CV-->>R: face(s)
    R->>T: add generated token
    R-->>A: {authenticated: true, token}
    A-->>C: {authenticated: true, token}
  else No face detected / invalid image
    R-->>A: 401 Unauthorized
    A-->>C: {detail: "No face detected. Access denied."}
  end
```

## Notes / constraints

- The token is stored only in server memory (`authenticated_users` set). If the server restarts, previously issued tokens stop working.
- This endpoint only checks whether *a face exists in the image* (not identity matching). It’s “presence detection”, not true face recognition.
- The token must be sent on later requests as an HTTP header named `token` (example: `token: <value>`).
