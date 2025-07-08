import cv2
import numpy as np

# Rango de color de piel en HSV (puede requerir ajuste según iluminación/piel)
lower_skin = np.array([0, 20, 70], dtype=np.uint8)
upper_skin = np.array([20, 255, 255], dtype=np.uint8)

def get_hand_center(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        roi = frame.copy()

        # Convertir a HSV y segmentar piel
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Tomar el contorno más grande (la mano)
            max_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_contour) > 3000:
                # Dibujar contorno
                cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)

                # Centroide de la mano
                center = get_hand_center(max_contour)
                if center:
                    cv2.circle(frame, center, 7, (255, 0, 0), -1)
                    cv2.putText(frame, 'Centro', (center[0]-20, center[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

                # Convex hull y defectos
                hull = cv2.convexHull(max_contour, returnPoints=False)
                if hull is not None and len(hull) > 3:
                    defects = cv2.convexityDefects(max_contour, hull)
                    if defects is not None:
                        count_defects = 0
                        for i in range(defects.shape[0]):
                            s, e, f, d = defects[i, 0]
                            start = tuple(max_contour[s][0])
                            end = tuple(max_contour[e][0])
                            far = tuple(max_contour[f][0])
                            # Calcular ángulo para filtrar defectos reales
                            a = np.linalg.norm(np.array(end) - np.array(start))
                            b = np.linalg.norm(np.array(far) - np.array(start))
                            c = np.linalg.norm(np.array(end) - np.array(far))
                            angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c + 1e-5))
                            if angle <= np.pi/2 and d > 10000:
                                count_defects += 1
                                cv2.circle(frame, far, 5, (0,0,255), -1)
                        # Decidir gesto
                        if count_defects >= 3:
                            gesture = "Mano Abierta"
                        else:
                            gesture = "Mano Cerrada"
                        cv2.putText(frame, gesture, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)
        
        cv2.imshow('Hand Gesture Recognition', frame)
        key = cv2.waitKey(1)
        if key == 27:  # ESC para salir
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 