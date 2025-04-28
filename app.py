from flask import Flask, render_template, request, make_response
import math
import csv
import io
import re


app = Flask(__name__)
def format_math_expression(expr):
    """
    Format mathematical expressions to proper LaTeX syntax with curly braces:
    u_i -> u_{i}
    u_i^j -> u_{i}^{j}
    """
    # Handle subscripts with multiple digits
    expr = re.sub(r'([a-zA-Z]+)_([0-9]+)', r'\1_{\2}', expr)
    # Handle superscripts with multiple digits
    expr = re.sub(r'([a-zA-Z]+)\^([0-9]+)', r'\1^{\2}', expr)
    # Handle combined subscripts and superscripts
    expr = re.sub(r'([a-zA-Z]+)_([0-9]+)\^([0-9]+)', r'\1_{\2}^{\3}', expr)
    """
    # Handle superscripts
    expr = re.sub(r'([a-zA-Z]+)\^([a-zA-Z0-9]+)', r'\1^{\2}', expr)
    # Handle subscripts
    expr = re.sub(r'([a-zA-Z]+)_([a-zA-Z0-9]+)', r'\1_{\2}', expr)
    """
    return expr

def calculate_res(n, m):
    base_value = (3 * n * m + 4 * n - 2) / 3
    ceil_value = math.ceil(base_value)
    
    n_mod6 = n % 6
    m_odd = m % 2 == 1
    
    condition1 = (n_mod6 in {0, 1, 2, 3} and m_odd) or (n_mod6 in {0, 2, 3, 5} and not m_odd)
    condition2 = (n_mod6 in {4, 5} and m_odd) or (n_mod6 in {1, 4} and not m_odd)
    
    if condition1:
        return ceil_value
    elif condition2:
        return ceil_value + 1
    else:
        return ceil_value

def label_vertex_u_v(i, m):
    if i == 1:
        return 0
    elif i == 2:
        return 2 * m
    else:
        return None  # Will be calculated by label_vertex_x

def label_vertex_c(i, m):
    if i == 1:
        if m % 2 == 1:
            return m + 1
        else:
            return m + 2
    elif i == 2:
        return 2 * m + 2
    else:
        return None  # Will be calculated by label_vertex_x

def label_vertex_u_v_j(i, j, m):
    if i == 1:
        return 0
    elif i == 2:
        if m % 2 == 1:
            return m + 3
        else:
            return m + 4
    else:
        return None  # Akan dihitung oleh label_vertex_x

def label_vertex_c_j(i, j, m):
    if i == 1:
        if m % 2 == 0:
            return m
        else:
            return m + 1
    elif i == 2:
        return 2 * m + 2
    else:
        return None  # Akan dihitung oleh label_vertex_x
    
def label_vertex_x(i, m):
    mod6 = i % 6
    if mod6 == 1 and m % 2 == 1 and i != 1:
        return (3 * i * m + 4 * i - 1) // 3
    elif mod6 == 1 and m % 2 == 0 and i != 1:
        return (3 * i * m + 4 * i + 2) // 3
    elif mod6 == 4:
        return (3 * i * m + 4 * i + 2) // 3
    elif mod6 == 2 and i != 2:
        return (3 * i * m + 4 * i - 2) // 3
    elif mod6 == 5 and m % 2 == 0:
        return (3 * i * m + 4 * i - 2) // 3
    elif mod6 == 3 and m % 2 == 1:
        return (3 * i * m + 4 * i - 3) // 3
    elif mod6 == 0 or (mod6 == 3 and m % 2 == 0):
        return (3 * i * m + 4 * i) // 3
    elif mod6 == 5 and m % 2 == 1:
        return (3 * i * m + 4 * i + 1) // 3
    else:
        return 0  # Default, shouldn't happen

def label_edge_uu(i, j, m):
    if i == 1 or (i == 2 and m % 2 == 0):
        return j
    elif i == 2 and m % 2 == 1:
        return j + 1
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 9) * m + 4 * i - 10) // 3 + j
        elif mod6 == 1 and m % 2 == 0 and i != 1 or mod6 == 4:
            return ((3 * i - 9) * m + 4 * i - 16) // 3 + j
        elif mod6 == 2 and i != 2 or (mod6 == 5 and m % 2 == 0):
            return ((3 * i - 9) * m + 4 * i - 8) // 3 + j
        elif mod6 == 0 or (mod6 == 3 and m % 2 == 0):
            return ((3 * i - 9) * m + 4 * i - 12) // 3 + j
        elif mod6 == 3 and m % 2 == 1:
            return ((3 * i - 9) * m + 4 * i - 6) // 3 + j
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 9) * m + 4 * i - 14) // 3 + j
        else:
            return 0  # Default

def label_edge_vv(i, j, m):
    if i == 1 or (i == 2 and m % 2 == 0):
        return m + j
    elif i == 2 and m % 2 == 1:
        return m + 1 + j
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 6) * m + 4 * i - 10) // 3 + j
        elif mod6 == 1 and m % 2 == 0 and i != 1 or mod6 == 4:
            return ((3 * i - 6) * m + 4 * i - 16) // 3 + j
        elif mod6 == 2 and i != 2 or (mod6 == 5 and m % 2 == 0):
            return ((3 * i - 6) * m + 4 * i - 8) // 3 + j
        elif mod6 == 0 or (mod6 == 3 and m % 2 == 0):
            return ((3 * i - 6) * m + 4 * i - 12) // 3 + j
        elif mod6 == 3 and m % 2 == 1:
            return ((3 * i - 6) * m + 4 * i - 6) // 3 + j
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 6) * m + 4 * i - 14) // 3 + j
        else:
            return 0  # Default

def label_edge_cc(i, j, m):
    if i == 1:
        return j
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 4) // 3 + j
        elif mod6 == 1 and m % 2 == 0 and i != 1 or mod6 == 4:
            return ((3 * i - 3) * m + 4 * i - 10) // 3 + j
        elif mod6 == 2 or (mod6 == 5 and m % 2 == 0):
            return ((3 * i - 3) * m + 4 * i - 2) // 3 + j
        elif mod6 == 0 or (mod6 == 3 and m % 2 == 0):
            return ((3 * i - 3) * m + 4 * i - 6) // 3 + j
        elif mod6 == 3 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i) // 3 + j
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 8) // 3 + j
        else:
            return 0  # Default

def label_edge_uc(i, m):
    if i == 1:
        if m % 2 == 1:
            return m
        else:
            return m - 1
    elif i == 2:
        return m + 3
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 7) // 3
        elif mod6 == 1 and m % 2 == 0 and i != 1 or mod6 == 4:
            return ((3 * i - 3) * m + 4 * i - 13) // 3
        elif mod6 == 2 or (mod6 == 5 and m % 2 == 0):
            return ((3 * i - 3) * m + 4 * i - 5) // 3
        elif mod6 == 0 or (mod6 == 3 and m % 2 == 0):
            return ((3 * i - 3) * m + 4 * i - 9) // 3
        elif mod6 == 3 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 3) // 3
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 11) // 3
        else:
            return 0  # Default

def label_edge_vc(i, m):
    if i == 1:
        if m % 2 == 1:
            return m + 1
        else:
            return m
    elif i == 2:
        return m + 4
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 4) // 3
        elif mod6 == 1 and m % 2 == 0 and i != 1 or mod6 == 4:
            return ((3 * i - 3) * m + 4 * i - 10) // 3
        elif mod6 == 2 or (mod6 == 5 and m % 2 == 0):
            return ((3 * i - 3) * m + 4 * i - 2) // 3
        elif mod6 == 0 or (mod6 == 3 and m % 2 == 0):
            return ((3 * i - 3) * m + 4 * i - 6) // 3
        elif mod6 == 3 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i) // 3
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 8) // 3
        else:
            return 0  # Default

def label_edge_cu(i, m):
    if i == 1:
        if m % 2 == 1:
            return 2
        else:
            return 1
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 4) // 3
        elif mod6 == 1 or mod6 == 4 and m % 2 == 0 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 7) // 3
        elif mod6 == 2 and m % 2 == 1 and i:
            return ((3 * i - 3) * m + 4 * i - 2) // 3
        elif mod6 == 2 or mod6 == 5 and m % 2 == 0:
            return ((3 * i - 3) * m + 4 * i - 5) // 3
        elif mod6 == 0 or mod6 == 3 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 6) // 3
        elif mod6 == 0 or mod6 == 3 and m % 2 == 0:
            return ((3 * i - 3) * m + 4 * i - 9) // 3
        elif mod6 == 4 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 10) // 3
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 8) // 3
        else:
            return 0  # Default

def label_edge_cv(i, m):
    if i == 1:
        if m % 2 == 1:
            return 3
        else:
            return 2
    else:
        mod6 = i % 6
        if mod6 == 1 and m % 2 == 1 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 1) // 3
        elif mod6 == 1 or mod6 == 4 and m % 2 == 0 and i != 1:
            return ((3 * i - 3) * m + 4 * i - 4) // 3
        elif mod6 == 2 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i + 1) // 3
        elif mod6 == 2 or mod6 == 5 and m % 2 == 0:
            return ((3 * i - 3) * m + 4 * i - 2) // 3
        elif mod6 == 0 or mod6 == 3 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 3) // 3
        elif mod6 == 0 or mod6 == 3 and m % 2 == 0:
            return ((3 * i - 3) * m + 4 * i - 6) // 3
        elif mod6 == 4 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 7) // 3
        elif mod6 == 5 and m % 2 == 1:
            return ((3 * i - 3) * m + 4 * i - 5) // 3
        else:
            return 0  # Default

def calculate_edge_weight_cu(i, m):
    return 3 * i * m + 4 * i - 1

def calculate_edge_weight_cv(i, m):
    return 3 * i * m + 4 * i

def calculate_edge_weight_uu(i, j, m):
    return (3 * i - 3) * m + 4 * i - 4 + j

def calculate_edge_weight_vv(i, j, m):
    return (3 * i - 2) * m + 4 * i - 4 + j

def calculate_edge_weight_uc(i, m):
    return (3 * i - 1) * m + 4 * i - 3

def calculate_edge_weight_vc(i, m):
    return (3 * i - 1) * m + 4 * i - 2

def calculate_edge_weight_cc(i, j, m):
    return (3 * i - 1) * m + 4 * i - 2 + j

@app.route('/export_csv')
def export_csv():
    if 'n' not in request.args or 'm' not in request.args:
        return "Parameter tidak valid"
    
    n = int(request.args['n'])
    m = int(request.args['m'])
    
    # Buat file CSV dalam memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Jenis', 'Nilai'])
    writer.writerow(['n', n])
    writer.writerow(['m', m])
    writer.writerow(['Jumlah Sisi', 3 * n * m + 4 * n - 2])
    writer.writerow(['res', calculate_res(n, m)])
    
    # Vertex labels
    writer.writerow([])
    writer.writerow(['Vertex', 'u_i', 'v_i', 'c_i', 'u_i_j', 'v_i_j', 'c_i_j'])
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            u_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
            v_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
            c_i = label_vertex_c(i, m) if i <= 2 else label_vertex_x(i, m)
            u_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
            v_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
            c_i_j = label_vertex_c_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
            writer.writerow([f'V{i}', u_i, v_i, c_i, u_i_j, v_i_j, c_i_j])

    #Edge labels
    writer.writerow([])
    writer.writerow(['Edge', 'uu', 'vv', 'cc', 'uc', 'vc', 'cu', 'cv'])
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            uu = label_edge_uu(i, j, m)
            vv = label_edge_vv(i, j, m)
            cc = label_edge_cc(i, j, m)
                    
            if j == m:
                uc = label_edge_uc(i, m)
                vc = label_edge_vc(i, m)
                        
                if i < n:
                    cu = label_edge_cu(i, m)
                    cv = label_edge_cv(i, m)
                    writer.writerow([f'{i}', uu, vv, cc, uc, vc, cu, cv])
                    
                else:
                    writer.writerow([f'{i}', uu, vv, cc, uc, vc, None, None])
                    
            else:
                writer.writerow([f'{i}', uu, vv, cc, None, None, None, None])

    #Edge weight
    writer.writerow([])
    writer.writerow(['i', 'j', 'sisi', 'x', 'xy', 'y', 'Bobot'])
    for i in range(1, n + 1):
        u_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
        v_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
        c_i = label_vertex_c(i, m) if i <= 2 else label_vertex_x(i, m)

        for j in range(1, m + 1):
            u_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
            uu = label_edge_uu(i, j, m)
            wt_uu = calculate_edge_weight_uu(i, j, m)
            writer.writerow([i, j, f"u_{i} u_{i} ^ {j}", u_i, uu, u_i_j, wt_uu])             

        for j in range(1, m + 1):
            v_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
            vv = label_edge_vv(i, j, m)
            wt_vv = calculate_edge_weight_vv(i, j, m)
            writer.writerow([i, j, f"v_{i} v_{i} ^ {j}", v_i, vv, v_i_j, wt_vv])         

        uc = label_edge_uc(i, m)
        vc = label_edge_vc(i, m)
        wt_uc = calculate_edge_weight_uc(i, m)
        wt_vc = calculate_edge_weight_vc(i, m)
        writer.writerow([i, None, f"u_{i} c_{i}", u_i, uc, c_i, wt_uc]) 
        writer.writerow([i, None, f"v_{i} c_{i}", v_i, vc, c_i, wt_vc]) 

        for j in range(1, m + 1):
            c_i_j = label_vertex_c_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
            cc = label_edge_cc(i, j, m)
            wt_cc = calculate_edge_weight_cc(i, j, m)
            writer.writerow([i, j, f"c_{i} c_{i} ^ {j}", c_i, cc, c_i_j, wt_cc])

        if i < n:
            cu = label_edge_cu(i, m)
            cv = label_edge_cv(i, m)
            next_u = label_vertex_u_v(i + 1, m) if i + 1 <= 2 else label_vertex_x(i + 1, m)
            next_v = label_vertex_u_v(i + 1, m) if i + 1 <= 2 else label_vertex_x(i + 1, m)
            wt_cu = calculate_edge_weight_cu(i, m)
            wt_cv = calculate_edge_weight_cv(i, m)
            writer.writerow([i, None, f"c_{i} u_{i}", c_i, cu, next_u, wt_cu])
            writer.writerow([i, None, f"c_{i} v_{i}", c_i, cv, next_v, wt_cv])

    # Konversi ke response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=graph_n{n}_m{m}.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            n = int(request.form['n'])
            m = int(request.form['m'])
            
            if n < 3 or m < 1:
                error = "Nilai tidak valid. Pastikan n >= 3 dan m >= 1"
                return render_template('index.html', error=error)
            
            # Calculate results
            jum_sisi = 3 * n * m + 4 * n - 2
            res = calculate_res(n, m)
            
            # Vertex labels
            vertex_labels = []
            for i in range(1, n + 1):
                u_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
                v_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
                c_i = label_vertex_c(i, m) if i <= 2 else label_vertex_x(i, m)
                """vertex_labels.append({
                        'i': i,
                        'u_i': u_i,
                        'v_i': v_i,
                        'c_i': c_i
                    })"""
                first_j_row = {
                    'i': i,
                    'j': 1,
                    'u_i': u_i,
                    'v_i': v_i,
                    'c_i': c_i,
                    'u_i_j': label_vertex_u_v_j(i, 1, m) if i <= 2 else label_vertex_x(i, m),
                    'v_i_j': label_vertex_u_v_j(i, 1, m) if i <= 2 else label_vertex_x(i, m),
                    'c_i_j': label_vertex_c_j(i, 1, m) if i <= 2 else label_vertex_x(i, m)
                }
                vertex_labels.append(first_j_row)

                for j in range(1, m):
                    #u_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
                    #v_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
                    #c_i_j = label_vertex_c_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
                    next_j_row = {
                        'i': i,
                        'j': j+1,
                        'u_i': '',
                        'v_i': '',
                        'c_i': '',
                        'u_i_j': label_vertex_u_v_j(i, j+1, m) if i <= 2 else label_vertex_x(i, m),
                        'v_i_j': label_vertex_u_v_j(i, j+1, m) if i <= 2 else label_vertex_x(i, m),
                        'c_i_j': label_vertex_c_j(i, j-1, m) if i <= 2 else label_vertex_x(i, m)
                    }
                    vertex_labels.append(next_j_row)
            
            # Edge labels
            edge_labels = []
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    uu = label_edge_uu(i, j, m)
                    vv = label_edge_vv(i, j, m)
                    cc = label_edge_cc(i, j, m)
                    
                    if j == m:
                        uc = label_edge_uc(i, m)
                        vc = label_edge_vc(i, m)
                        
                        if i < n:
                            cu = label_edge_cu(i, m)
                            cv = label_edge_cv(i, m)
                            edge_labels.append({
                                'i': i,
                                'j': j,
                                'uu': uu,
                                'vv': vv,
                                'cc': cc,
                                'uc': uc,
                                'vc': vc,
                                'cu': cu,
                                'cv': cv
                            })
                        else:
                            edge_labels.append({
                                'i': i,
                                'j': j,
                                'uu': uu,
                                'vv': vv,
                                'cc': cc,
                                'uc': uc,
                                'vc': vc,
                                'cu': None,
                                'cv': None
                            })
                    else:
                        edge_labels.append({
                            'i': i,
                            'j': j,
                            'uu': uu,
                            'vv': vv,
                            'cc': cc,
                            'uc': None,
                            'vc': None,
                            'cu': None,
                            'cv': None
                        })
            
            # Edge weights
            edge_weights = []
            for i in range(1, n + 1):
                u_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
                v_i = label_vertex_u_v(i, m) if i <= 2 else label_vertex_x(i, m)
                c_i = label_vertex_c(i, m) if i <= 2 else label_vertex_x(i, m)

                for j in range(1, m + 1):
                    u_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
                    uu = label_edge_uu(i, j, m)
                    wt_uu = calculate_edge_weight_uu(i, j, m)
                    edge_weights.append({
                        'i': i,
                        'j': j,
                        'x': f"φ({format_math_expression(f'u_{i}')}) = {u_i}", #f"φ(u_{i}) = {u_i}",
                        #'xy': f"φ({format_math_expression(f'u_{i}u_{i}^{j}')}) = {uu}", #f"φ(u_{i}u_{i}^{j}) = {uu}",
                        'xy': f"φ({format_math_expression(f'u_{i} u_{i}^ {j}')}) = {uu}",
                        'y': f"φ({format_math_expression(f'u_{i}^ {j}')}) = {u_i_j}", #f"φ(u_{i}^{j}) = {u_i_j}",
                        'weight': wt_uu
                    })

                for j in range(1, m + 1):
                    v_i_j = label_vertex_u_v_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
                    vv = label_edge_vv(i, j, m)
                    wt_vv = calculate_edge_weight_vv(i, j, m)
                    edge_weights.append({
                        'i': i,
                        'j': j,
                        'x': f"φ({format_math_expression(f'v_{i}')}) = {v_i}", #f"φ(v_{i}) = {v_i}",
                        'xy': f"φ({format_math_expression(f'v_{i} v_{i}^ {j}')}) = {vv}", #f"φ(v_{{i}}v_{{i}}^{{j}}) = {vv}",
                        'y': f"φ({format_math_expression(f'v_{i}^{j}')}) = {v_i_j}", #f"φ(v_{i}^{j}) = {v_i_j}",
                        'weight': wt_vv
                    })

                uc = label_edge_uc(i, m)
                vc = label_edge_vc(i, m)
                wt_uc = calculate_edge_weight_uc(i, m)
                wt_vc = calculate_edge_weight_vc(i, m)
                edge_weights.append({
                    'i': i,
                    'x': f"φ({format_math_expression(f'u_{i}')}) = {u_i}", #f"φ(u_{i}) = {u_i}",
                    'xy': f"φ({format_math_expression(f'u_{i} c_{i}')}) = {uc}", #f"φ(u_{i}c_{i}) = {uc}",
                    'y': f"φ({format_math_expression(f'c_{i}')}) = {c_i}", #f"φ(c_{i}) = {c_i}",
                    'weight': wt_uc
                })
                edge_weights.append({
                    'i': i,
                    'x': f"φ({format_math_expression(f'v_{i}')}) = {v_i}", #f"φ(v_{i}) = {v_i}",
                    'xy': f"φ({format_math_expression(f'v_{i} c_{i}')}) = {vc}", #f"φ(v_{i}c_{i}) = {vc}",
                    'y': f"φ({format_math_expression(f'c_{i}')}) = {c_i}", #f"φ(c_{i}) = {c_i}",
                    'weight': wt_vc
                })

                for j in range(1, m + 1):
                    c_i_j = label_vertex_c_j(i, j, m) if i <= 2 else label_vertex_x(i, m)
                    cc = label_edge_cc(i, j, m)
                    wt_cc = calculate_edge_weight_cc(i, j, m)
                    edge_weights.append({
                        'i': i,
                        'j': j,
                        'x': f"φ({format_math_expression(f'c_{i}')}) = {c_i}", #f"φ(c_{i}) = {c_i}",
                        'xy': f"φ({format_math_expression(f'c_{i} c_{i}^{j}')}) = {cc}", #f"φ(c_{i}c_{i}^{j}) = {cc}",
                        'y': f"φ({format_math_expression(f'c_{i}^{j}')}) = {c_i_j}", #f"φ(c_{i}^{j}) = {c_i_j}",
                        'weight': wt_cc
                    })

                if i < n:
                    cu = label_edge_cu(i, m)
                    cv = label_edge_cv(i, m)
                    next_u = label_vertex_u_v(i + 1, m) if i + 1 <= 2 else label_vertex_x(i + 1, m)
                    next_v = label_vertex_u_v(i + 1, m) if i + 1 <= 2 else label_vertex_x(i + 1, m)
                    wt_cu = calculate_edge_weight_cu(i, m)
                    wt_cv = calculate_edge_weight_cv(i, m)
                    edge_weights.append({
                        'i': i,
                        'x': f"φ({format_math_expression(f'c_{i}')}) = {c_i}", #f"φ(c_{i}) = {c_i}",
                        'xy': f"φ({format_math_expression(f'c_{i} u_{i+1}')}) = {cu}", #f"φ(c_{i}u_{i+1}) = {cu}",
                        'y': f"φ({format_math_expression(f'u_{i+1}')}) = {next_u}", #f"φ(u_{i+1}) = {next_u}",
                        'weight': wt_cu
                    })
                    edge_weights.append({
                        'i': i,
                        'x': f"φ({format_math_expression(f'c_{i}')}) = {c_i}", #f"φ(c_{i}) = {c_i}",
                        'xy': f"φ({format_math_expression(f'c_{i} v_{i+1}')}) = {cv}", 
                        'y': f"φ({format_math_expression(f'v_{i+1}')}) = {next_v}", #f"φ(v_{i+1}) = {next_v}",
                        'weight': wt_cv
                    })
            
            return render_template('index.html', 
                                n=n, 
                                m=m, 
                                jum_sisi=jum_sisi, 
                                res=res,
                                vertex_labels=vertex_labels,
                                edge_labels=edge_labels,
                                edge_weights=edge_weights)
        
        except ValueError:
            error = "Masukkan harus berupa bilangan bulat"
            return render_template('index.html', error=error)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
