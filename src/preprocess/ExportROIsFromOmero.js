//https://gist.github.com/Yu-AnChen/58754f960ccd540e307ed991bc6901b0
//Execution
// In google chrome, go the omero and make sure you are logged in
// In any of your chrome tab/window, hit F12 to launch the developer tools (FN -> F12 KEY)
// In the console tab of the DevTools paste in the contents of the export_omero_roi.js script
// Replace the 7-digit omero image ID in the imgIds list with your image ID
// Hit enter to run, it will ask you to save a csv file, your ROIs will be in there.


var imgIds = [
    697372,
];
const omeroUrls = {
    nyu: 'https://omero.nyumc.org',
};
// choose omero instance between the HMS and the IDP OMERO
const whichOmero = 'nyu';

// add 1 sec pause for each 10-download batch
imgIds.forEach((el, idx) => setTimeout(() => export_roi_by_id(el, omeroUrls[whichOmero.toLowerCase()]), idx * 200));

function export_roi_by_id(imgId, omeroUrl) {

    var omeroUrl = omeroUrl;
    var headers = ['Id', 'Name', 'Text', 'type', 'all_points', 'X', 'Y', 'RadiusX', 'RadiusY', 'Width', 'Height', 'all_transforms'];
    var url = `${omeroUrl}/api/v0/m/images/${imgId}/`;
    var urlRoi = `${omeroUrl}/api/v0/m/images/${imgId}/rois/?limit=500`;
    var imgName;

    fetch(url)
        .then(res => res.json())
        .then(resJson =>
            imgName = resJson.data.Name
        )
        .then(() => fetch(urlRoi)
            .then(res => res.json())
            .then(resJson =>
                resJson.data
                    // exclude roi that does not contain shapes
                    .filter(data => data.shapes)
                    .map(data => {
                        data.shapes[0].Name = data.Name || 'undefined';
                        data.shapes[0].Id = data['@id'];
                        return data.shapes;
                    })
                    .reduce((acc, val) => acc.concat(val), [])
                    // .filter(shape => shape['@type'].includes('Rect'))
                    .map(shape => {
                        shape.type = shape['@type'].split('#').pop();
                        shape.all_points = getPointsOfShape(shape);
                        shape.all_transforms = shape.Transform
                            ? [
                                shape.Transform.A00, shape.Transform.A01, shape.Transform.A02,
                                shape.Transform.A10, shape.Transform.A11, shape.Transform.A12,
                                0, 0, 1
                            ].join(',')
                            : -1;
                        return shape;
                    })
                    .map(shape => headers.map(header => JSON.stringify(shape[header]) || -1))
            )
            .then(rois => rois.map(e => e.join(",")).join("\n"))
            .then(roisStr =>
                "data:text/csv;charset=utf-8," +
                headers.join(',') + '\n' +
                roisStr.replace(/#/g, '-'))
            .then(fullStr => encodeURI(fullStr))
            .then(uri => {
                let link = document.createElement("a");
                link.setAttribute("href", uri);
                link.setAttribute("download", `${imgName}-${imgId}-rois.csv`);
                document.body.appendChild(link);
                link.click();
            })
        )
}

function getPointsOfShape(shape) {
    let all_points = [];
    if (shape['@type'].includes('Line')) {
        const T = shape.Transform;
        all_points = [
            transformPoint(shape.X1, shape.Y1, T),
            transformPoint(shape.X2, shape.Y2, T)
        ];
    }
    if (shape['@type'].includes('Poly')) {
        const T = shape.Transform;
        all_points = shape.Points.split(' ').map(
            xy => xy.split(',').map(cc => parseFloat(cc))
        ).map(xy => transformPoint(...xy, T));
    }
    if (shape['@type'].includes('Rect')) {
        const [X, Y] = [shape.X, shape.Y];
        const [W, H] = [shape.Width, shape.Height];
        const T = shape.Transform;
        all_points = [
            transformPoint(X, Y, T),
            transformPoint(X + W, Y, T),
            transformPoint(X + W, Y + H, T),
            transformPoint(X, Y + H, T)
        ];
    }
    if (shape['@type'].includes('Ellipse')) {
        const [Rx, Ry] = [shape.RadiusX, shape.RadiusY];
        const [Cx, Cy] = [shape.X, shape.Y];
        const T = shape.Transform;
        all_points = [
            transformPoint(Cx + Rx, Cy, T),
            transformPoint(Cx - Rx, Cy, T),
            transformPoint(Cx, Cy + Ry, T),
            transformPoint(Cx, Cy - Ry, T),
        ];
    }
    if (shape['@type'].includes('Point')) {
        const T = shape.Transform;
        all_points = [
            transformPoint(shape.X, shape.Y, T)
        ];
    }
    if (!all_points.length) {
        console.warn(
            `ROI ${shape.Name} of type ${shape.type} is not fully supported yet in this script, validation is needed.`
        );
    }
    all_points = all_points.map(point => point.join(',')).join(' ');
    return all_points;
}
function transformPoint(x, y, t) {
    t = t
        ? t
        : { A00: 1, A01: 0, A02: 0, A10: 0, A11: 1, A12: 0 };
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    const point = svg.createSVGPoint();
    point.x = x;
    point.y = y;
    const transform = svg.createSVGMatrix();
    transform.a = t.A00;
    transform.b = t.A10;
    transform.c = t.A01;
    transform.d = t.A11;
    transform.e = t.A02;
    transform.f = t.A12;
    return [
        point.matrixTransform(transform).x.toFixed(3),
        point.matrixTransform(transform).y.toFixed(3)
    ];
}

function getUpperLeft() {
    let args = [...arguments];
    return [
        Math.min(...args.map(el => el.x)),
        Math.min(...args.map(el => el.y))
    ];
}
function getLowerRight() {
    let args = [...arguments];
    return [
        Math.max(...args.map(el => el.x)),
        Math.max(...args.map(el => el.y))
    ];
}