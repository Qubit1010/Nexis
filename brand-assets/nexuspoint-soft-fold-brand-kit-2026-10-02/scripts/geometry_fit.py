"""Adaptive curve fitting for native contour geometry. Source rasters are read only."""
import math
import numpy as np
import cv2
from skimage import measure

def unit(v):
    n = np.linalg.norm(v)
    return v / n if n else v

def bez(c, t):
    return (1-t)**3*c[0] + 3*(1-t)**2*t*c[1] + 3*(1-t)*t*t*c[2] + t**3*c[3]

def generate(points, us, left, right):
    a = np.array([3*u*(1-u)**2*left for u in us])
    b = np.array([3*u*u*(1-u)*right for u in us])
    c00, c01, c11 = np.sum(a*a), np.sum(a*b), np.sum(b*b)
    residual = np.array([p-((1-u)**3+3*u*(1-u)**2)*points[0]-(u**3+3*u*u*(1-u))*points[-1] for p,u in zip(points,us)])
    x0, x1 = np.sum(a*residual), np.sum(b*residual)
    det = c00*c11-c01*c01
    alpha0 = (x0*c11-x1*c01)/det if abs(det)>1e-12 else 0
    alpha1 = (c00*x1-c01*x0)/det if abs(det)>1e-12 else 0
    seg = np.linalg.norm(points[-1]-points[0])
    if alpha0 < 1e-6*seg or alpha1 < 1e-6*seg:
        alpha0=alpha1=seg/3
    return np.array([points[0], points[0]+alpha0*left, points[-1]+alpha1*right, points[-1]])

def params(points):
    us=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    return us/us[-1] if us[-1] else np.linspace(0,1,len(points))

def error(points,c,us):
    errs=np.array([np.dot(bez(c,u)-p,bez(c,u)-p) for p,u in zip(points,us)])
    split=int(np.argmax(errs[1:-1]))+1 if len(errs)>2 else 1
    return float(errs[split]),split

def refine(points,c,us):
    d1=3*np.diff(c,axis=0)
    d2=2*np.diff(d1,axis=0)
    out=[]
    for p,u in zip(points,us):
        q=bez(c,u)
        q1=(1-u)**2*d1[0]+2*(1-u)*u*d1[1]+u*u*d1[2]
        q2=(1-u)*d2[0]+u*d2[1]
        r=q-p
        den=np.dot(q1,q1)+np.dot(r,q2)
        out.append(np.clip(u-np.dot(r,q1)/den,0,1) if abs(den)>1e-12 else u)
    return np.array(out)

def fit(points,left,right,tolerance=0.65):
    if len(points)==2:
        d=np.linalg.norm(points[0]-points[1])/3
        return [np.array([points[0],points[0]+left*d,points[1]+right*d,points[1]])]
    us=params(points)
    c=generate(points,us,left,right)
    e,split=error(points,c,us)
    if e<tolerance*tolerance:
        return [c]
    if e<4*tolerance*tolerance:
        for _ in range(6):
            us=refine(points,c,us)
            if np.any(np.diff(us)<0): break
            c=generate(points,us,left,right)
            e,split=error(points,c,us)
            if e<tolerance*tolerance:return [c]
    center=unit(points[split-1]-points[split+1])
    return fit(points[:split+1],left,center,tolerance)+fit(points[split:],-center,right,tolerance)

def fmt(n):
    return f'{float(n):.3f}'.rstrip('0').rstrip('.')

def contour_path(contour):
    # Retain dense marching-square samples during fitting. Removing collinear
    # samples before fitting permits Bezier overshoot between corner endpoints.
    pts=np.array(contour[:,::-1],dtype=float)
    # Start on a corner rather than splitting a smooth arc across the closing seam.
    angles=[]
    for i in range(len(pts)):
        a,b=unit(pts[i]-pts[i-1]),unit(pts[(i+1)%len(pts)]-pts[i])
        angles.append(math.acos(np.clip(np.dot(a,b),-1,1)))
    start=int(np.argmax(angles))
    pts=np.roll(pts,-start,axis=0)
    pts=np.vstack([pts,pts[0]])
    curves=fit(pts,unit(pts[1]-pts[0]),unit(pts[-2]-pts[-1]))
    parts=[f'M{fmt(curves[0][0][0])},{fmt(curves[0][0][1])}']
    for c in curves:
        # Preserve straight faces as line commands when controls lie on the segment.
        v=c[3]-c[0]
        cross=lambda p: v[0]*p[1]-v[1]*p[0]
        dist=max(abs(cross(c[1]-c[0])),abs(cross(c[2]-c[0])))/(np.linalg.norm(v) or 1)
        if dist < 0.1:
            parts.append(f'L{fmt(c[3][0])},{fmt(c[3][1])}')
        else:
            parts.append('C'+','.join(fmt(x) for x in c[1:].reshape(-1)))
    return ' '.join(parts)+' Z'

def paths_for(mask, bounds):
    x0,y0,x1,y1=bounds
    field=mask[y0:y1,x0:x1].astype(float)
    contours=measure.find_contours(field,160)
    result=[]
    for contour in contours:
        contour[:,0]+=y0
        contour[:,1]+=x0
        area=cv2.contourArea(contour[:,::-1].astype(np.float32))
        if area>8:result.append(contour_path(contour))
    return result

