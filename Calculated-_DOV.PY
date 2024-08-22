import os
import glob
import numpy as np
import netCDF4 as nc
import pandas as pd
import math
########################################################################################################################
#求解某两点间的方位角
def calculate_azimuth(lat1, lon1, lat2, lon2):
    d2r = math.pi / 180.0  # 将角度转换为弧度
    latm = (lat2 + lat1) * 0.5 * d2r
    lon_diff = (lon2 - lon1) * d2r  # 经度差值的弧度
    lat1_rad = lat1 * d2r
    lat2_rad = lat2 * d2r

    dlat= (lat2_rad-lat1_rad) * d2r
    dlon = lon_diff * np.cos(latm) * d2r

    azimuth_rad = math.atan2(dlon, dlat)  # 计算方位角的弧度值
    azimuth_deg = math.degrees(azimuth_rad)  # 将弧度转换为度数

    return azimuth_deg
########################################################################################################################
#进行粗差剔除
def remove_outliers(grid_data, factor='标定'):
    valid_data = grid_data[~np.isnan(grid_data)]  # 提取非NaN值的数据

    mean = np.mean(valid_data)  # 计算数据的均值
    mad = np.median(np.abs(valid_data - mean))    # 计算数据的中误差（Median Absolute Deviation，MAD）
    threshold = factor * mad   # 计算剔除的阈值

    # 计算异常值的下限和上限
    lower_bound = mean - threshold
    upper_bound = mean + threshold

    # 标识异常值并将其剔除
    mask = (grid_data >= lower_bound) & (grid_data <= upper_bound)
    cleaned_data = np.where(mask, grid_data, np.nan)

    return cleaned_data
########################################################################################################################
# 读取移去-恢复的大地水准面高数据.nc数据 格网大小为1′
data = nc.Dataset(ref_geoid)
lon = data.variables["lon"][:].data
lat = data.variables["lat"][:].data
#
xgm_geoid = data.variables["z"][:].data
# 构建二维格网数据
# repeat
lon11 = lon.reshape(1, lon.size)
lon11 = np.repeat(lon11, lat.size, 0)

lat11 = lat.reshape(lat.size, 1)
lat11 = np.repeat(lat11, lon.size, 1)

# 读取nc数据 mss 格网大小为1′
CLS_mss_data = nc.Dataset(mss)  # 获取nc文件的所有数据
# 提取数据
lon2 = CLS_mss_data.variables["x"][:].data
lat2 = CLS_mss_data.variables["y"][:].data
mss3_data = CLS_mss_data.variables["z"][:].data
mss_std = np.std(mss3_data)
mss_max = np.max(mss3_data)
mss_min = np.min(mss3_data)
mss_mean = np.mean(mss3_data)
#
path_4 = path_2[:-2]+'txt'  # 随意
# 读取nc，mdt，已进行线性插值，格网大小为1′
mdt_data = nc.Dataset(mdt)
# 提取数据
lon3 = mdt_data.variables["x"][:].data
lat3 = mdt_data.variables["y"][:].data
mdt3_data = mdt_data.variables["z"][:].data
m, n = xgm_griod.shape
# 无滤波和3中误差剔除处理!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
sy_geoid = mss3_data - mdt3_data - xgm_griod
# sy_geoid[np.isnan(sy_geoid)] = 0
# std1=np.std(sy_geoid)
########################################################################################################################
# 执行异常值剔除
cleaned_data = remove_outliers(sy_geoid, factor=15.0)

# 执行异常值剔除前的数据数量
before_removal_count = np.sum(~np.isnan(sy_geoid))

# 执行异常值剔除后的数据数量
after_removal_count = np.sum(~np.isnan(cleaned_data))

print("剔除前的数据数量:", before_removal_count)
print("剔除后的数据数量:", after_removal_count)
sy_geoid = cleaned_data
sy_geoid[np.isnan(sy_geoid)] = 0
std1 = np.std(sy_geoid)
print('sy_geoid_std = ', std1)
# plt.imshow(sy_geoid,vmin=-0.5,vmax=0.5)

gridlat1 = lat11
gridlon1 = lon11

num_rows_lat = lon.size  # 需要复制的行数
# 将一列数据复制为多行相同数据
lat_11 = lat.reshape(-1, 1)
lat_1 = np.repeat(lat_11, num_rows_lat, axis=1)
# 将一行数据复制为多行相同数据
num_rows_lon = lat.size
lon_1 = np.tile(lon, (num_rows_lon, 1))
########################################################################################################################
###################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
########################################################################################################################
###################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
########################################################################################################################
# 求出某两点之间的球面距离
a, b = sy_geoid.shape
DD_k = np.zeros((a - 4, b - 4))
DD_dict = {}  # 创建一个空字典用于存储结果
# lat1_dict={}
# lon1_dict={}
# lat2_dict={}
# lon2_dict={}
slices_i = [(0, -4), (1, -3), (2, -2)]
for start, end in slices_i:
    lat1_rad = lat_1[start:end, :]
    lon1_rad = lon_1[start:end, :]
    if abs(start) == 0:
        start = -a
    lat2_rad = lat_1[-end:-start, :]
    lon2_rad = lon_1[-end:-start, :]
    #    print(lat1_rad.shape)
    #    print(lon1_rad.shape)
    #    print(lat2_rad.shape)
    #    print(lon2_rad.shape)
    slices_j = [(0, -4), (1, -3), (2, -2), (3, -1), (4, 0)]
    if start == 2 and end == -2:
        slices_j = [(0, -4), (1, -3)]
    for start1, end1 in slices_j:
        if abs(end1) == 0:
            end1 = b
        lat1_rad_rad = lat1_rad[:, start1:end1]
        lon1_rad_rad = lon1_rad[:, start1:end1]
        if abs(start1) == 0:
            start1 = -b
        lat2_rad_rad = lat2_rad[:, -end1:-start1]
        lon2_rad_rad = lon2_rad[:, -end1:-start1]
        #        name1 = f"lat1_{str(start)}_{str(end)}_{str(start1)}_{str(end1)}"
        #        name2 = f"lon1_{str(start)}_{str(end)}_{str(start1)}_{str(end1)}"
        #        name3 = f"lat2_{str(start)}_{str(end)}_{str(start1)}_{str(end1)}"
        #        name4 = f"lon2_{str(start)}_{str(end)}_{str(start1)}_{str(end1)}"
        #        lat1_dict[name1] = lat1_rad_rad  # 将结果存储到字典中
        #        lon1_dict[name2] = lon1_rad_rad
        #        lat2_dict[name3] = lat2_rad_rad
        #        lon2_dict[name4] = lon2_rad_rad
        # print("done")
        for m in np.arange(a - 4):  # 1857
            for n in np.arange(b - 4):  # 1917
                DD_k[m, n] = calculate_geodesic_distance(lat1_rad_rad[m, n], lon1_rad_rad[m, n], lat2_rad_rad[m, n],
                                                         lon2_rad_rad[m, n])
                print(m, n)
        name = f"DD_{str(start)}_{str(end)}_{str(start1)}_{str(end1)}"

        temp = np.array(DD_k)
        DD_dict[name] = temp
        #         生成一个唯一的名称
        # 将结果存储到字典中
        print("ddk done", m)
print("done")
########################################################################################################################
DD_name1 = f"DD_-{str(a)}_-4_-{str(b)}_-4"
DD_24_1 = DD_dict[DD_name1]
DD_name2 = f"DD_-{str(a)}_-4_1_-3"
DD_23_2 = DD_dict[DD_name2]
DD_name3 = f"DD_-{str(a)}_-4_2_-2"
DD_22_3 = DD_dict[DD_name3]
DD_name4 = f"DD_-{str(a)}_-4_3_-1"
DD_21_4 = DD_dict[DD_name4]
DD_name5 = f"DD_-{str(a)}_-4_4_{str(b)}"
DD_20_5 = DD_dict[DD_name5]
DD_name6 = f"DD_1_-3_-{str(b)}_-4"
DD_19_6 = DD_dict[DD_name6]
DD_name7 = f"DD_1_-3_1_-3"
DD_18_7 = DD_dict[DD_name7]
DD_name8 = f"DD_1_-3_2_-2"
DD_17_8 = DD_dict[DD_name8]
DD_name9 = f"DD_1_-3_3_-1"
DD_16_9 = DD_dict[DD_name9]
DD_name10 = f"DD_1_-3_4_{str(b)}"
DD_15_10 = DD_dict[DD_name10]
DD_name11 = f"DD_2_-2_-{str(b)}_-4"
DD_14_11 = DD_dict[DD_name11]
DD_name12 = f"DD_2_-2_1_-3"
DD_13_12 = DD_dict[DD_name12]
########################################################################################################################
# 求出某两点之间的方位角
a, b = sy_geoid.shape
az_k = np.zeros((a - 4, b - 4))
az_dict = {}  # 创建一个空字典用于存储结果
slices_i = [(0, -4), (1, -3), (2, -2)]
for start, end in slices_i:
    lat1_rad = lat_1[start:end, :]
    lon1_rad = lon_1[start:end, :]
    if abs(start) == 0:
        start = -a
    lat2_rad = lat_1[-end:-start, :]
    lon2_rad = lon_1[-end:-start, :]
    slices_j = [(0, -4), (1, -3), (2, -2), (3, -1), (4, 0)]
    if start == 2 and end == -2:
        slices_j = [(0, -4), (1, -3)]
    for start1, end1 in slices_j:
        if abs(end1) == 0:
            end1 = b
        lat1_rad_rad = lat1_rad[:, start1:end1]
        lon1_rad_rad = lon1_rad[:, start1:end1]
        if abs(start1) == 0:
            start1 = -b
        lat2_rad_rad = lat2_rad[:, -end1:-start1]
        lon2_rad_rad = lon2_rad[:, -end1:-start1]
        for m in np.arange(a - 4):
            for n in np.arange(b - 4):
                az_k[m, n] = calculate_azimuth(lat1_rad_rad[m, n], lon1_rad_rad[m, n], lat2_rad_rad[m, n],
                                               lon2_rad_rad[m, n])
                print(m, n)
        name = f"az_{str(start)}_{str(end)}_{str(start1)}_{str(end1)}"

        temp = np.array(az_k)
        az_dict[name] = temp
        #         生成一个唯一的名称
        # 将结果存储到字典中

        print("azk done", m)
print("done")
########################################################################################################################
# 假设要访问名为"az_0_-4_-4_0"的结果矩阵
az_name1 = f"az_-{str(a)}_-4_-{str(b)}_-4"
az_24_1 = az_dict[az_name1]
az_name2 = f"az_-{str(a)}_-4_1_-3"
az_23_2 = az_dict[az_name2]
az_name3 = f"az_-{str(a)}_-4_2_-2"
az_22_3 = az_dict[az_name3]
az_name4 = f"az_-{str(a)}_-4_3_-1"
az_21_4 = az_dict[az_name4]
az_name5 = f"az_-{str(a)}_-4_4_{str(b)}"
az_20_5 = az_dict[az_name5]
az_name6 = f"az_1_-3_-{str(b)}_-4"
az_19_6 = az_dict[az_name6]
az_name7 = "az_1_-3_1_-3"
az_18_7 = az_dict[az_name7]
az_name8 = "az_1_-3_2_-2"
az_17_8 = az_dict[az_name8]
az_name9 = "az_1_-3_3_-1"
az_16_9 = az_dict[az_name9]
az_name10 = f"az_1_-3_4_{str(b)}"
az_15_10 = az_dict[az_name10]
az_name11 = f"az_2_-2_-{str(b)}_-4"
az_14_11 = az_dict[az_name11]
az_name12 = "az_2_-2_1_-3"
az_13_12 = az_dict[az_name12]
########################################################################################################################
# 开始计算梯度
a, b = sy_geoid.shape
rho = 206264.8062
# 计算的梯度（24-1）
# 求出point(24)-point(1)之间的梯度
e_24_1 = (sy_geoid[4:, 4:] - sy_geoid[:-4, :-4]) / DD_24_1 * rho
# 求出point(23)-point(2)之间的梯度
e_23_2 = (sy_geoid[4:, 3:-1] - sy_geoid[:-4, 1:-3]) / DD_23_2 * rho
# 求出point(22)-point(3)之间的梯度
e_22_3 = (sy_geoid[4:, 2:-2] - sy_geoid[:-4, 2:-2]) / DD_22_3 * rho
# 求出point(21)-point(4)之间的梯度
e_21_4 = (sy_geoid[4:, 1:-3] - sy_geoid[:-4, 3:-1]) / DD_21_4 * rho
# 求出point(20)-point(5)之间的梯度
e_20_5 = (sy_geoid[4:, :-4] - sy_geoid[:-4, 4:]) / DD_20_5 * rho
# 求出point(19)-point(6)之间的梯度
e_19_6 = (sy_geoid[3:-1, 4:] - sy_geoid[1:-3, :-4]) / DD_19_6 * rho
# 求出point(18)-point(7)之间的梯度
e_18_7 = (sy_geoid[3:-1, 3:-1] - sy_geoid[1:-3, 1:-3]) / DD_18_7 * rho
# 求出point(17)-point(8)之间的梯度
e_17_8 = (sy_geoid[3:-1, 2:-2] - sy_geoid[1:-3, 2:-2]) / DD_17_8 * rho
# 求出point(16)-point(9)之间的梯度
e_16_9 = (sy_geoid[3:-1, 1:-3] - sy_geoid[1:-3, 3:-1]) / DD_16_9 * rho
# 求出point(15)-point(10)之间的梯度
e_15_10 = (sy_geoid[3:-1, :-4] - sy_geoid[1:-3, 4:]) / DD_15_10 * rho
# 求出point(14)-point(11)之间的梯度
e_14_11 = (sy_geoid[2:-2, 4:] - sy_geoid[2:-2, :-4]) / DD_14_11 * rho
# 求出point(13)-point(12)之间的梯度
e_13_12 = (sy_geoid[2:-2, 3:-1] - sy_geoid[2:-2, 1:-3]) / DD_13_12 * rho
########################################################################################################################
########################################################################################################################
# (外扩展2个格网).定义已知数据,求解最小二乘最优解
g_sn = np.zeros((a - 4, b - 4))
g_ew = np.zeros((a - 4, b - 4))
for i in np.arange(a - 4):
    for j in np.arange(b - 4):
        v = np.array([(e_24_1[i, j] + e_18_7[i, j]) / 2 \
                         , e_23_2[i, j] \
                         , (e_22_3[i, j] + e_17_8[i, j]) / 2 \
                         , e_21_4[i, j] \
                         , (e_20_5[i, j] + e_16_9[i, j]) / 2 \
                         , e_19_6[i, j] \
                         , e_15_10[i, j] \
                         , (e_14_11[i, j] + e_13_12[i, j]) / 2])  # v₁, v₂, v₃
        # alpha = np.array([315 or 135,0 or 180,45 or 225,90 or 270])  # α₁, α₂, α₃
        alpha = np.array(
            [math.radians(180 - az_24_1[i, j]), math.radians(180 - az_23_2[i, j]), math.radians(180 - az_22_3[i, j]) \
                , math.radians(180 - az_21_4[i, j]), math.radians(180 - az_20_5[i, j]),
             math.radians(180 - az_19_6[i, j]) \
                , math.radians(180 - az_15_10[i, j]), math.radians(az_14_11[i, j])])  # α₁, α₂, α₃
########################################################################################################################
########################################################################################################################
        # 构建矩阵 A
        A = np.column_stack((np.cos(alpha), np.sin(alpha)))

        # 求解 ξ 和 η
        X = np.linalg.inv(A.T @ A) @ A.T @ v

        # 提取结果
        g_sn[i, j] = -X[0]
        g_ew[i, j] = X[1]
########################################################################################################################
##存储为TXT格式
# 另外两个数组可以直接使用原始的二维数组作为结果
g_sn_lat = gridlat1[2:-2, 2:-2]
g_sn_lon = gridlon1[2:-2, 2:-2]

# 另外两个数组可以直接使用原始的二维数组作为结果
g_ew_lat = gridlat1[2:-2, 2:-2]
g_ew_lon = gridlon1[2:-2, 2:-2]
# 上面格网数据相应的经纬度如下：
g_lat = g_ew_lat
g_lon = g_ew_lon

# 保存出去
g_lon1 = g_lon.reshape(g_lon.size, 1)
g_lat1 = g_lat.reshape(g_lat.size, 1)

g_sn1 = g_sn.reshape(g_sn.size, 1)
g_ew1 = g_ew.reshape(g_ew.size, 1)

g_sn1[np.isnan(g_sn1)] = 0
g_ew1[np.isnan(g_ew1)] = 0

g_sn_points = np.hstack((g_lon1, g_lat1))
g_ew_points = np.hstack((g_lon1, g_lat1))

g_sn_values = np.hstack((g_sn_points, g_sn1))
g_ew_values = np.hstack((g_ew_points, g_ew1))

filename = os.path.basename(path_4)

start_index = filename.find('_') + 1
end_index = filename.find('.txt')
region_string = filename[start_index:end_index]
#
save_path_ns = os.path.dirname(os.path.dirname(path_4)) + '/sy_DOV/' + 'g_ns_' + region_string + '.txt'
save_path_ew = os.path.dirname(os.path.dirname(path_4)) + '/sy_DOV/' + 'g_ew_' + region_string + '.txt'
# 使用 savetxt() 函数保存数组为文本文件
np.savetxt(save_path_ns, g_sn_values, fmt=['%.8f', '%.8f', '%.12f'], delimiter='    ')
np.savetxt(save_path_ew, g_ew_values, fmt=['%.8f', '%.8f', '%.12f'], delimiter='    ')
print('done')